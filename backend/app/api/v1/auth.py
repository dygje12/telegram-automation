from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import (
    AuthResponse,
    ErrorResponse,
    LoginRequest,
    MessageResponseGeneric,
    Verify2FARequest,
    VerifyCodeRequest,
)
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        payload = auth_service.verify_token(token)

        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = auth_service.get_user_by_id(db, int(user_id))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/login", response_model=MessageResponseGeneric)
async def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    """Start login process by sending verification code"""
    try:
        # Check if user exists, if not create one
        existing_user = auth_service.get_user_by_phone(db, login_request.phone_number)
        if not existing_user:
            # Register new user
            await auth_service.register_user(
                db, login_request.api_id, login_request.api_hash, login_request.phone_number
            )

        # Start login process
        result = await auth_service.start_login(db, login_request)

        return MessageResponseGeneric(message=result["message"], success=True)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/verify-code")
async def verify_code(verify_request: VerifyCodeRequest, db: Session = Depends(get_db)):
    """Verify authentication code"""
    try:
        result = await auth_service.verify_code(db, verify_request)

        if result.get("requires_2fa"):
            return MessageResponseGeneric(message=result["message"], success=True)
        else:
            # Return auth response
            return AuthResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/verify-2fa")
async def verify_2fa(verify_request: Verify2FARequest, db: Session = Depends(get_db)):
    """Verify 2FA password"""
    try:
        result = await auth_service.verify_2fa(db, verify_request)
        return AuthResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/status")
async def get_auth_status(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current authentication status"""
    try:
        status_info = await auth_service.get_auth_status(db, current_user.id)
        return status_info

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/logout", response_model=MessageResponseGeneric)
async def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Logout user"""
    try:
        await auth_service.logout(db, current_user.id)

        return MessageResponseGeneric(message="Successfully logged out", success=True)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user information"""
    try:
        from app.utils.encryption import encryption_manager

        return {
            "id": current_user.id,
            "phone_number": encryption_manager.decrypt(current_user.phone_number),
            "created_at": current_user.created_at,
            "updated_at": current_user.updated_at,
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
