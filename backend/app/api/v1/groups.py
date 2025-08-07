from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.routers.auth import get_current_user
from app.schemas import ErrorResponse, GroupCreate, GroupResponse, MessageResponseGeneric
from app.services.group_service import group_service

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("/", response_model=List[GroupResponse])
async def get_groups(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all groups for current user"""
    try:
        if search:
            groups = group_service.search_groups(db, current_user.id, search)
        elif active_only:
            groups = group_service.get_active_groups(db, current_user.id)
        else:
            groups = group_service.get_groups(db, current_user.id, skip, limit)

        return groups

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/stats")
async def get_group_stats(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get group statistics"""
    try:
        stats = group_service.get_group_count(db, current_user.id)
        return stats

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get a specific group"""
    try:
        group = group_service.get_group_by_id(db, group_id, current_user.id)

        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

        return group

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/", response_model=GroupResponse)
async def add_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a new group with validation"""
    try:
        group = await group_service.add_group(db, group_data, current_user.id)
        return group

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{group_id}", response_model=MessageResponseGeneric)
async def remove_group(
    group_id: int,
    permanent: bool = Query(False, description="Permanently delete the group"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a group (soft delete by default, permanent if specified)"""
    try:
        if permanent:
            success = group_service.delete_group(db, group_id, current_user.id)
            message = "Group permanently deleted"
        else:
            success = group_service.remove_group(db, group_id, current_user.id)
            message = "Group removed (deactivated)"

        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

        return MessageResponseGeneric(message=message, success=True)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{group_id}/toggle", response_model=GroupResponse)
async def toggle_group_status(
    group_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Toggle group active status"""
    try:
        group = group_service.toggle_group_status(db, group_id, current_user.id)

        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

        return group

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{group_id}/validate")
async def validate_group(
    group_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Validate group access and update information"""
    try:
        result = await group_service.validate_group(db, group_id, current_user.id)
        return result

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/validate-all")
async def validate_all_groups(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Validate all active groups"""
    try:
        result = await group_service.validate_all_groups(db, current_user.id)
        return result

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
