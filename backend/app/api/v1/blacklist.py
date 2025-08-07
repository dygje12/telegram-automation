from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.database import get_db
from app.models import BlacklistResponse, MessageResponseGeneric, User
from app.services.blacklist_service import blacklist_service

router = APIRouter(prefix="/blacklist", tags=["blacklist"])


@router.get("/", response_model=List[BlacklistResponse])
async def get_blacklist(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True, description="Show only active (non-expired) blacklist entries"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get blacklisted groups for current user"""
    try:
        if active_only:
            blacklist_entries = blacklist_service.get_active_blacklist(db, current_user.id)
        else:
            blacklist_entries = blacklist_service.get_blacklist(db, current_user.id, skip, limit)

        return blacklist_entries

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/stats")
async def get_blacklist_stats(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get blacklist statistics"""
    try:
        stats = blacklist_service.get_blacklist_stats(db, current_user.id)
        return stats

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{blacklist_id}", response_model=MessageResponseGeneric)
async def remove_from_blacklist(
    blacklist_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Remove a group from blacklist manually"""
    try:
        success = blacklist_service.remove_from_blacklist(db, blacklist_id, current_user.id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Blacklist entry not found"
            )

        return MessageResponseGeneric(
            message="Group removed from blacklist successfully", success=True
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/cleanup", response_model=MessageResponseGeneric)
async def cleanup_expired_blacklist(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Clean up expired blacklist entries"""
    try:
        count = blacklist_service.cleanup_expired_blacklist(db, current_user.id)

        return MessageResponseGeneric(
            message=f"Cleaned up {count} expired blacklist entries", success=True
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/recently-unblacklisted")
async def get_recently_unblacklisted(
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get groups that were recently removed from blacklist"""
    try:
        group_ids = blacklist_service.get_recently_unblacklisted(db, current_user.id, hours)

        return {"group_ids": group_ids, "count": len(group_ids), "hours_back": hours}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/group/{group_id}/remove", response_model=MessageResponseGeneric)
async def remove_group_from_blacklist(
    group_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Remove a specific group from blacklist by group ID"""
    try:
        success = blacklist_service.remove_group_from_blacklist(db, current_user.id, group_id)

        if not success:
            return MessageResponseGeneric(message="Group was not in blacklist", success=True)

        return MessageResponseGeneric(
            message="Group removed from blacklist successfully", success=True
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/group/{group_id}/check")
async def check_group_blacklist_status(
    group_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Check if a specific group is blacklisted"""
    try:
        is_blacklisted = blacklist_service.is_group_blacklisted(db, current_user.id, group_id)

        # Get blacklist entry details if blacklisted
        blacklist_entry = None
        if is_blacklisted:
            from datetime import datetime

            now = datetime.utcnow()

            blacklist_entry = (
                db.query(app.models.Blacklist)
                .filter(
                    app.models.Blacklist.user_id == current_user.id,
                    app.models.Blacklist.group_id == group_id,
                    (app.models.Blacklist.blacklist_type == "permanent")
                    | (app.models.Blacklist.expires_at > now),
                )
                .first()
            )

        result = {"group_id": group_id, "is_blacklisted": is_blacklisted}

        if blacklist_entry:
            result.update(
                {
                    "blacklist_type": blacklist_entry.blacklist_type,
                    "reason": blacklist_entry.reason,
                    "expires_at": blacklist_entry.expires_at,
                    "created_at": blacklist_entry.created_at,
                }
            )

        return result

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
