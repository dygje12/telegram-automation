from sqlalchemy.orm import Session
from app.models import Blacklist, Group, User
from typing import List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class BlacklistService:
    def __init__(self):
        pass
    
    def get_blacklist(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Blacklist]:
        """Get all blacklisted groups for a user"""
        return db.query(Blacklist).filter(
            Blacklist.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    def get_active_blacklist(self, db: Session, user_id: int) -> List[Blacklist]:
        """Get currently active blacklisted groups (not expired)"""
        now = datetime.utcnow()
        
        return db.query(Blacklist).filter(
            Blacklist.user_id == user_id,
            (Blacklist.blacklist_type == 'permanent') |
            (Blacklist.expires_at > now)
        ).all()
    
    def is_group_blacklisted(self, db: Session, user_id: int, group_id: str) -> bool:
        """Check if a group is currently blacklisted"""
        now = datetime.utcnow()
        
        blacklist_entry = db.query(Blacklist).filter(
            Blacklist.user_id == user_id,
            Blacklist.group_id == group_id,
            (Blacklist.blacklist_type == 'permanent') |
            (Blacklist.expires_at > now)
        ).first()
        
        return blacklist_entry is not None
    
    def add_to_blacklist(self, db: Session, user_id: int, group_id: str, 
                        blacklist_type: str, reason: str = None, 
                        duration_seconds: int = None) -> Blacklist:
        """Add a group to blacklist"""
        try:
            # Check if user exists
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise Exception("User not found")
            
            # Remove existing blacklist entry for this group
            existing = db.query(Blacklist).filter(
                Blacklist.user_id == user_id,
                Blacklist.group_id == group_id
            ).first()
            
            if existing:
                db.delete(existing)
            
            # Calculate expiration time for temporary blacklist
            expires_at = None
            if blacklist_type == 'temporary' and duration_seconds:
                expires_at = datetime.utcnow() + timedelta(seconds=duration_seconds)
            
            # Create blacklist entry
            blacklist_entry = Blacklist(
                user_id=user_id,
                group_id=group_id,
                blacklist_type=blacklist_type,
                reason=reason,
                expires_at=expires_at
            )
            
            db.add(blacklist_entry)
            db.commit()
            db.refresh(blacklist_entry)
            
            logger.info(f"Added group {group_id} to {blacklist_type} blacklist for user {user_id}")
            
            return blacklist_entry
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to add group to blacklist: {str(e)}")
            raise Exception(f"Failed to add group to blacklist: {str(e)}")
    
    def remove_from_blacklist(self, db: Session, blacklist_id: int, user_id: int) -> bool:
        """Remove a group from blacklist"""
        try:
            blacklist_entry = db.query(Blacklist).filter(
                Blacklist.id == blacklist_id,
                Blacklist.user_id == user_id
            ).first()
            
            if not blacklist_entry:
                raise Exception("Blacklist entry not found")
            
            group_id = blacklist_entry.group_id
            db.delete(blacklist_entry)
            db.commit()
            
            logger.info(f"Removed group {group_id} from blacklist for user {user_id}")
            
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to remove group from blacklist: {str(e)}")
            raise Exception(f"Failed to remove group from blacklist: {str(e)}")
    
    def remove_group_from_blacklist(self, db: Session, user_id: int, group_id: str) -> bool:
        """Remove a group from blacklist by group ID"""
        try:
            blacklist_entry = db.query(Blacklist).filter(
                Blacklist.user_id == user_id,
                Blacklist.group_id == group_id
            ).first()
            
            if not blacklist_entry:
                return False
            
            db.delete(blacklist_entry)
            db.commit()
            
            logger.info(f"Removed group {group_id} from blacklist for user {user_id}")
            
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to remove group from blacklist: {str(e)}")
            return False
    
    def cleanup_expired_blacklist(self, db: Session, user_id: int = None) -> int:
        """Clean up expired temporary blacklist entries"""
        try:
            now = datetime.utcnow()
            
            query = db.query(Blacklist).filter(
                Blacklist.blacklist_type == 'temporary',
                Blacklist.expires_at <= now
            )
            
            if user_id:
                query = query.filter(Blacklist.user_id == user_id)
            
            expired_entries = query.all()
            count = len(expired_entries)
            
            for entry in expired_entries:
                logger.info(f"Cleaning up expired blacklist entry for group {entry.group_id}")
                db.delete(entry)
            
            db.commit()
            
            logger.info(f"Cleaned up {count} expired blacklist entries")
            
            return count
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to cleanup expired blacklist: {str(e)}")
            return 0
    
    def get_blacklist_stats(self, db: Session, user_id: int) -> dict:
        """Get blacklist statistics"""
        now = datetime.utcnow()
        
        total = db.query(Blacklist).filter(Blacklist.user_id == user_id).count()
        
        permanent = db.query(Blacklist).filter(
            Blacklist.user_id == user_id,
            Blacklist.blacklist_type == 'permanent'
        ).count()
        
        temporary_active = db.query(Blacklist).filter(
            Blacklist.user_id == user_id,
            Blacklist.blacklist_type == 'temporary',
            Blacklist.expires_at > now
        ).count()
        
        temporary_expired = db.query(Blacklist).filter(
            Blacklist.user_id == user_id,
            Blacklist.blacklist_type == 'temporary',
            Blacklist.expires_at <= now
        ).count()
        
        return {
            "total": total,
            "permanent": permanent,
            "temporary_active": temporary_active,
            "temporary_expired": temporary_expired,
            "active": permanent + temporary_active
        }
    
    def handle_telegram_error(self, db: Session, user_id: int, group_id: str, error: Exception) -> bool:
        """Handle Telegram errors and add to blacklist accordingly"""
        try:
            error_str = str(error).lower()
            
            # SlowModeWaitError - temporary blacklist
            if 'slowmodewait' in error_str or 'slow mode' in error_str:
                # Extract wait time from error message
                import re
                match = re.search(r'(\d+)', error_str)
                wait_seconds = int(match.group(1)) if match else 60  # Default 1 minute if not specified
                # Ensure wait_seconds does not exceed 60 minutes (3600 seconds) for slow mode
                wait_seconds = min(wait_seconds, 3600)
                
                self.add_to_blacklist(
                    db, user_id, group_id, 'temporary',
                    reason=f"Slow mode active: {error_str}",
                    duration_seconds=wait_seconds
                )
                return True
            
            # FloodWaitError - temporary blacklist
            elif 'floodwait' in error_str or 'flood wait' in error_str:
                # Extract wait time from error message
                import re
                match = re.search(r'(\d+)', error_str)
                wait_seconds = int(match.group(1)) if match else 3600  # Default 1 hour
                # For flood wait, we can keep the default 1 hour or more as it's a server-side limit
                
                self.add_to_blacklist(
                    db, user_id, group_id, 'temporary',
                    reason=f"Flood wait: {error_str}",
                    duration_seconds=wait_seconds
                )
                return True
            
            # Permanent errors
            elif any(keyword in error_str for keyword in [
                'chatwriteforbidden', 'userbannedinchannel', 'chatadminrequired',
                'peeridinvalid', 'forbidden', 'banned', 'no permission'
            ]):
                self.add_to_blacklist(
                    db, user_id, group_id, 'permanent',
                    reason=f"Permanent error: {error_str}"
                )
                return True
            
            # Unknown error - temporary blacklist for safety
            else:
                self.add_to_blacklist(
                    db, user_id, group_id, 'temporary',
                    reason=f"Unknown error: {error_str}",
                    duration_seconds=3600  # 1 hour
                )
                return True
                
        except Exception as e:
            logger.error(f"Failed to handle Telegram error: {str(e)}")
            return False
    
    def get_recently_unblacklisted(self, db: Session, user_id: int, hours: int = 24) -> List[str]:
        """Get groups that were recently removed from blacklist"""
        try:
            # This is a simplified implementation
            # In a real scenario, you might want to keep a separate log of unblacklist events
            since = datetime.utcnow() - timedelta(hours=hours)
            
            # For now, we'll return groups that had temporary blacklist entries that expired recently
            # This is not perfect but gives an idea of recently available groups
            
            expired_entries = db.query(Blacklist).filter(
                Blacklist.user_id == user_id,
                Blacklist.blacklist_type == 'temporary',
                Blacklist.expires_at > since,
                Blacklist.expires_at <= datetime.utcnow()
            ).all()
            
            return [entry.group_id for entry in expired_entries]
            
        except Exception as e:
            logger.error(f"Failed to get recently unblacklisted groups: {str(e)}")
            return []

# Global instance
blacklist_service = BlacklistService()

