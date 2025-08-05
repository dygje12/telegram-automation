from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, Message, Group, Log, Settings
from app.services.telegram_service import telegram_service
from app.services.blacklist_service import blacklist_service
from app.utils.encryption import encryption_manager
from telethon.errors import SlowModeWaitError, FloodWaitError
import asyncio
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.running_jobs: Dict[int, str] = {}  # user_id -> job_id
        self.job_stats: Dict[int, dict] = {}  # user_id -> stats
    
    def start_scheduler(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
    
    async def start_user_job(self, user_id: int) -> bool:
        """Start message sending job for a user"""
        try:
            # Stop existing job if running
            await self.stop_user_job(user_id)
            
            # Get user settings
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    raise Exception("User not found")
                
                settings = db.query(Settings).filter(Settings.user_id == user_id).first()
                if not settings:
                    # Create default settings
                    settings = Settings(user_id=user_id)
                    db.add(settings)
                    db.commit()
                    db.refresh(settings)
                
                # Calculate random interval
                interval_seconds = random.randint(settings.min_interval, settings.max_interval)
                
                # Add job to scheduler
                job = self.scheduler.add_job(
                    self._send_messages_job,
                    IntervalTrigger(seconds=interval_seconds),
                    args=[user_id],
                    id=f"user_{user_id}",
                    replace_existing=True,
                    max_instances=1
                )
                
                self.running_jobs[user_id] = job.id
                self.job_stats[user_id] = {
                    "started_at": datetime.utcnow(),
                    "last_run": None,
                    "next_run": job.next_run_time,
                    "total_messages_sent": 0,
                    "total_errors": 0,
                    "interval_seconds": interval_seconds
                }
                
                logger.info(f"Started message sending job for user {user_id} with interval {interval_seconds}s")
                return True
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to start job for user {user_id}: {str(e)}")
            return False
    
    async def stop_user_job(self, user_id: int) -> bool:
        """Stop message sending job for a user"""
        try:
            job_id = self.running_jobs.get(user_id)
            if job_id:
                self.scheduler.remove_job(job_id)
                del self.running_jobs[user_id]
                if user_id in self.job_stats:
                    del self.job_stats[user_id]
                logger.info(f"Stopped message sending job for user {user_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to stop job for user {user_id}: {str(e)}")
            return False
    
    def is_user_job_running(self, user_id: int) -> bool:
        """Check if user job is running"""
        return user_id in self.running_jobs
    
    def get_user_job_status(self, user_id: int) -> Optional[dict]:
        """Get user job status"""
        if user_id not in self.job_stats:
            return None
        
        stats = self.job_stats[user_id].copy()
        
        # Update next run time from scheduler
        job_id = self.running_jobs.get(user_id)
        if job_id:
            job = self.scheduler.get_job(job_id)
            if job:
                stats["next_run"] = job.next_run_time
        
        return stats
    
    async def _send_messages_job(self, user_id: int):
        """Main job function to send messages"""
        db = SessionLocal()
        try:
            logger.info(f"Starting message sending cycle for user {user_id}")
            
            # Update job stats
            if user_id in self.job_stats:
                self.job_stats[user_id]["last_run"] = datetime.utcnow()
            
            # Clean up expired blacklist entries
            blacklist_service.cleanup_expired_blacklist(db, user_id)
            
            # Get user and check if authenticated
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.session_data:
                logger.warning(f"User {user_id} not authenticated, stopping job")
                await self.stop_user_job(user_id)
                return
            
            # Ensure Telegram client is connected
            client = await telegram_service.get_client(user_id)
            if not client:
                try:
                    decrypted_api_id = encryption_manager.decrypt(user.api_id)
                    decrypted_api_hash = encryption_manager.decrypt(user.api_hash)
                    
                    await telegram_service.create_client(
                        user_id, decrypted_api_id, decrypted_api_hash, user.session_data
                    )
                    client = await telegram_service.get_client(user_id)
                except Exception as e:
                    logger.error(f"Failed to create Telegram client for user {user_id}: {str(e)}")
                    return
            
            if not client:
                logger.error(f"Could not establish Telegram client for user {user_id}")
                return
            
            # Get active messages
            active_messages = db.query(Message).filter(
                Message.user_id == user_id,
                Message.is_active == True
            ).all()
            
            if not active_messages:
                logger.info(f"No active messages for user {user_id}")
                return
            
            # Get active groups (not blacklisted)
            active_groups = db.query(Group).filter(
                Group.user_id == user_id,
                Group.is_active == True
            ).all()
            
            if not active_groups:
                logger.info(f"No active groups for user {user_id}")
                return
            
            # Filter out blacklisted groups
            available_groups = []
            for group in active_groups:
                if not blacklist_service.is_group_blacklisted(db, user_id, group.group_id):
                    available_groups.append(group)
            
            if not available_groups:
                logger.info(f"All groups are blacklisted for user {user_id}")
                return
            
            # Select random message and group
            selected_message = random.choice(active_messages)
            selected_group = random.choice(available_groups)
            
            # Get user settings for delay
            settings = db.query(Settings).filter(Settings.user_id == user_id).first()
            if settings:
                delay = random.randint(settings.min_delay, settings.max_delay)
            else:
                delay = random.randint(5, 10)
            
            logger.info(f"Sending message '{selected_message.title}' to group '{selected_group.group_name}' for user {user_id}")
            
            # Apply random delay
            await asyncio.sleep(delay)
            
            # Send message
            try:
                await telegram_service.send_message(
                    client, selected_group.group_id, selected_message.content
                )
                
                # Log success
                log_entry = Log(
                    user_id=user_id,
                    group_id=selected_group.group_id,
                    message_id=selected_message.id,
                    status='success'
                )
                db.add(log_entry)
                db.commit()
                
                # Update stats
                if user_id in self.job_stats:
                    self.job_stats[user_id]["total_messages_sent"] += 1
                
                logger.info(f"Successfully sent message to group {selected_group.group_id} for user {user_id}")
                
            except (SlowModeWaitError, FloodWaitError) as e:
                # Handle rate limiting errors
                logger.warning(f"Rate limiting error for group {selected_group.group_id}: {str(e)}")
                
                # Add to blacklist
                blacklist_service.handle_telegram_error(db, user_id, selected_group.group_id, e)
                
                # Log error
                log_entry = Log(
                    user_id=user_id,
                    group_id=selected_group.group_id,
                    message_id=selected_message.id,
                    status='blacklisted',
                    error_message=str(e)
                )
                db.add(log_entry)
                db.commit()
                
                # Update stats
                if user_id in self.job_stats:
                    self.job_stats[user_id]["total_errors"] += 1
                
            except Exception as e:
                # Handle other errors
                logger.error(f"Error sending message to group {selected_group.group_id}: {str(e)}")
                
                # Add to blacklist based on error type
                blacklist_service.handle_telegram_error(db, user_id, selected_group.group_id, e)
                
                # Log error
                log_entry = Log(
                    user_id=user_id,
                    group_id=selected_group.group_id,
                    message_id=selected_message.id,
                    status='failed',
                    error_message=str(e)
                )
                db.add(log_entry)
                db.commit()
                
                # Update stats
                if user_id in self.job_stats:
                    self.job_stats[user_id]["total_errors"] += 1
            
            # Schedule next interval with randomization
            if user_id in self.running_jobs:
                job_id = self.running_jobs[user_id]
                job = self.scheduler.get_job(job_id)
                if job and settings:
                    # Update interval for next run
                    new_interval = random.randint(settings.min_interval, settings.max_interval)
                    job.reschedule(IntervalTrigger(seconds=new_interval))
                    
                    if user_id in self.job_stats:
                        self.job_stats[user_id]["interval_seconds"] = new_interval
            
        except Exception as e:
            logger.error(f"Error in message sending job for user {user_id}: {str(e)}")
            
            if user_id in self.job_stats:
                self.job_stats[user_id]["total_errors"] += 1
                
        finally:
            db.close()
    
    def get_all_job_stats(self) -> Dict[int, dict]:
        """Get stats for all running jobs"""
        return self.job_stats.copy()
    
    async def restart_all_jobs(self):
        """Restart all running jobs (useful after server restart)"""
        db = SessionLocal()
        try:
            # Get all users who should have jobs running
            # This would typically be stored in a separate table or configuration
            # For now, we'll just restart jobs for users who have active messages and groups
            
            users_with_active_data = db.query(User).join(Message).join(Group).filter(
                Message.is_active == True,
                Group.is_active == True
            ).distinct().all()
            
            for user in users_with_active_data:
                await self.start_user_job(user.id)
                
        finally:
            db.close()

# Global instance
scheduler_service = SchedulerService()

