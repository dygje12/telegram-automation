from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Settings, User
from app.routers.auth import get_current_user
from app.schemas import MessageResponseGeneric, SettingsResponse, SettingsUpdate

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/", response_model=SettingsResponse)
async def get_settings(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user settings"""
    try:
        settings = db.query(Settings).filter(Settings.user_id == current_user.id).first()

        if not settings:
            # Create default settings
            settings = Settings(user_id=current_user.id)
            db.add(settings)
            db.commit()
            db.refresh(settings)

        return settings

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/", response_model=SettingsResponse)
async def update_settings(
    settings_data: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user settings"""
    try:
        settings = db.query(Settings).filter(Settings.user_id == current_user.id).first()

        if not settings:
            # Create new settings if doesn't exist
            settings = Settings(user_id=current_user.id)
            db.add(settings)

        # Update fields
        if settings_data.min_interval is not None:
            settings.min_interval = settings_data.min_interval

        if settings_data.max_interval is not None:
            settings.max_interval = settings_data.max_interval

        if settings_data.min_delay is not None:
            settings.min_delay = settings_data.min_delay

        if settings_data.max_delay is not None:
            settings.max_delay = settings_data.max_delay

        # Validate interval relationship
        if settings.min_interval > settings.max_interval:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum interval cannot be greater than maximum interval",
            )

        # Validate delay relationship
        if settings.min_delay > settings.max_delay:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum delay cannot be greater than maximum delay",
            )

        settings.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(settings)

        return settings

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/reset", response_model=SettingsResponse)
async def reset_settings(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Reset settings to default values"""
    try:
        settings = db.query(Settings).filter(Settings.user_id == current_user.id).first()

        if not settings:
            settings = Settings(user_id=current_user.id)
            db.add(settings)
        else:
            # Reset to defaults
            settings.min_interval = 4200  # 1 hour 10 minutes
            settings.max_interval = 5400  # 1 hour 30 minutes
            settings.min_delay = 5  # 5 seconds
            settings.max_delay = 10  # 10 seconds
            settings.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(settings)

        return settings

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/intervals/presets")
async def get_interval_presets():
    """Get predefined interval presets"""
    try:
        presets = [
            {
                "name": "Conservative",
                "description": "Longer intervals for maximum safety",
                "min_interval": 7200,  # 2 hours
                "max_interval": 10800,  # 3 hours
                "min_delay": 10,
                "max_delay": 30,
            },
            {
                "name": "Default",
                "description": "Balanced intervals as recommended",
                "min_interval": 4200,  # 1 hour 10 minutes
                "max_interval": 5400,  # 1 hour 30 minutes
                "min_delay": 5,
                "max_delay": 10,
            },
            {
                "name": "Moderate",
                "description": "Shorter intervals for more frequent sending",
                "min_interval": 2700,  # 45 minutes
                "max_interval": 3600,  # 1 hour
                "min_delay": 3,
                "max_delay": 8,
            },
            {
                "name": "Aggressive",
                "description": "Minimum safe intervals (use with caution)",
                "min_interval": 1800,  # 30 minutes
                "max_interval": 2700,  # 45 minutes
                "min_delay": 2,
                "max_delay": 5,
            },
        ]

        return {"presets": presets}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/intervals/apply-preset", response_model=SettingsResponse)
async def apply_interval_preset(
    preset_name: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Apply a predefined interval preset"""
    try:
        # Get presets
        presets_response = await get_interval_presets()
        presets = {p["name"]: p for p in presets_response["presets"]}

        if preset_name not in presets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid preset name. Available presets: {list(presets.keys())}",
            )

        preset = presets[preset_name]

        # Update settings
        settings_update = SettingsUpdate(
            min_interval=preset["min_interval"],
            max_interval=preset["max_interval"],
            min_delay=preset["min_delay"],
            max_delay=preset["max_delay"],
        )

        return await update_settings(settings_update, current_user, db)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/validation")
async def validate_settings(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Validate current settings and provide recommendations"""
    try:
        settings = db.query(Settings).filter(Settings.user_id == current_user.id).first()

        if not settings:
            return {
                "valid": False,
                "message": "No settings found. Default settings will be created.",
                "recommendations": [],
            }

        recommendations = []
        warnings = []

        # Check intervals
        if settings.min_interval < 1800:  # Less than 30 minutes
            warnings.append("Very short intervals may trigger Telegram's anti-spam measures")
            recommendations.append("Consider using intervals of at least 30 minutes")

        if settings.max_interval > 86400:  # More than 24 hours
            warnings.append(
                "Very long intervals may reduce message sending frequency significantly"
            )

        # Check delays
        if settings.min_delay < 2:
            warnings.append("Very short delays may appear bot-like")
            recommendations.append("Consider using delays of at least 2 seconds")

        if settings.max_delay > 300:  # More than 5 minutes
            warnings.append("Very long delays may slow down the sending process")

        # Check relationships
        interval_range = settings.max_interval - settings.min_interval
        if interval_range < 600:  # Less than 10 minutes difference
            recommendations.append(
                "Consider increasing the interval range for better randomization"
            )

        return {
            "valid": len(warnings) == 0,
            "warnings": warnings,
            "recommendations": recommendations,
            "current_settings": {
                "min_interval": settings.min_interval,
                "max_interval": settings.max_interval,
                "min_delay": settings.min_delay,
                "max_delay": settings.max_delay,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
