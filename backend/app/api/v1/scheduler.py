from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.database import get_db
from app.models import Log, LogResponse, MessageResponseGeneric, SchedulerStatus, User
from app.services.blacklist_service import blacklist_service
from app.services.group_service import group_service
from app.services.message_service import message_service
from app.services.scheduler_service import scheduler_service

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


@router.post("/start", response_model=MessageResponseGeneric)
async def start_scheduler(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Start automatic message sending for current user"""
    try:
        # Check if user has active messages and groups
        active_messages = message_service.get_active_messages(db, current_user.id)
        active_groups = group_service.get_active_groups(db, current_user.id)

        if not active_messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active messages found. Please add and activate at least one message template.",
            )

        if not active_groups:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active groups found. Please add at least one group.",
            )

        # Check if any groups are available (not blacklisted)
        available_groups = []
        for group in active_groups:
            if not blacklist_service.is_group_blacklisted(db, current_user.id, group.group_id):
                available_groups.append(group)

        if not available_groups:
            return MessageResponseGeneric(
                message="All groups are currently blacklisted. Scheduler started but will wait for groups to become available.",
                success=True,
            )

        # Start the scheduler job
        success = await scheduler_service.start_user_job(current_user.id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to start scheduler",
            )

        return MessageResponseGeneric(
            message=f"Scheduler started successfully. Found {len(active_messages)} active messages and {len(available_groups)} available groups.",
            success=True,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/stop", response_model=MessageResponseGeneric)
async def stop_scheduler(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Stop automatic message sending for current user"""
    try:
        success = await scheduler_service.stop_user_job(current_user.id)

        if not success:
            return MessageResponseGeneric(message="Scheduler was not running", success=True)

        return MessageResponseGeneric(message="Scheduler stopped successfully", success=True)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/status", response_model=SchedulerStatus)
async def get_scheduler_status(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get scheduler status for current user"""
    try:
        is_running = scheduler_service.is_user_job_running(current_user.id)
        job_status = scheduler_service.get_user_job_status(current_user.id)

        # Get statistics
        total_messages = message_service.get_message_count(db, current_user.id)
        total_groups = group_service.get_group_count(db, current_user.id)
        blacklist_stats = blacklist_service.get_blacklist_stats(db, current_user.id)

        # Count recent successful sends
        from datetime import datetime, timedelta

        recent_logs = (
            db.query(Log)
            .filter(
                Log.user_id == current_user.id,
                Log.status == "success",
                Log.created_at >= datetime.utcnow() - timedelta(days=1),
            )
            .count()
        )

        status = SchedulerStatus(
            is_running=is_running,
            next_run=job_status.get("next_run") if job_status else None,
            last_run=job_status.get("last_run") if job_status else None,
            total_messages_sent=(
                job_status.get("total_messages_sent", 0) if job_status else recent_logs
            ),
            total_groups=total_groups["total"],
            active_groups=total_groups["active"] - blacklist_stats["active"],
            blacklisted_groups=blacklist_stats["active"],
        )

        return status

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/logs", response_model=List[LogResponse])
async def get_scheduler_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    status_filter: Optional[str] = Query(
        None, description="Filter by status: success, failed, blacklisted"
    ),
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get recent scheduler logs"""
    try:
        from datetime import datetime, timedelta

        since = datetime.utcnow() - timedelta(hours=hours)

        query = db.query(Log).filter(Log.user_id == current_user.id, Log.created_at >= since)

        if status_filter:
            query = query.filter(Log.status == status_filter)

        logs = query.order_by(Log.created_at.desc()).offset(skip).limit(limit).all()

        return logs

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/logs/stats")
async def get_log_stats(
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get log statistics"""
    try:
        from datetime import datetime, timedelta

        since = datetime.utcnow() - timedelta(hours=hours)

        total = (
            db.query(Log).filter(Log.user_id == current_user.id, Log.created_at >= since).count()
        )

        success = (
            db.query(Log)
            .filter(
                Log.user_id == current_user.id, Log.created_at >= since, Log.status == "success"
            )
            .count()
        )

        failed = (
            db.query(Log)
            .filter(Log.user_id == current_user.id, Log.created_at >= since, Log.status == "failed")
            .count()
        )

        blacklisted = (
            db.query(Log)
            .filter(
                Log.user_id == current_user.id, Log.created_at >= since, Log.status == "blacklisted"
            )
            .count()
        )

        return {
            "total": total,
            "success": success,
            "failed": failed,
            "blacklisted": blacklisted,
            "success_rate": (success / total * 100) if total > 0 else 0,
            "hours": hours,
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/restart", response_model=MessageResponseGeneric)
async def restart_scheduler(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Restart scheduler for current user"""
    try:
        # Stop if running
        await scheduler_service.stop_user_job(current_user.id)

        # Start again
        success = await scheduler_service.start_user_job(current_user.id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to restart scheduler",
            )

        return MessageResponseGeneric(message="Scheduler restarted successfully", success=True)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
