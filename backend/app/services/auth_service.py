import os
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models import Settings, User
from app.schemas import LoginRequest, UserCreate, Verify2FARequest, VerifyCodeRequest
from app.services.telegram_service import telegram_service
from app.utils.encryption import encryption_manager
from app.utils.validators import normalize_phone_number, validate_api_credentials

load_dotenv()

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self):
        pass

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None

    def get_user_by_phone(self, db: Session, phone_number: str) -> Optional[User]:
        """Get user by phone number"""
        # Normalize phone number
        normalized_phone = normalize_phone_number(phone_number)

        # Since phone numbers are encrypted, we need to check all users
        users = db.query(User).all()
        for user in users:
            try:
                decrypted_phone = encryption_manager.decrypt(user.phone_number)
                if normalize_phone_number(decrypted_phone) == normalized_phone:
                    return user
            except:
                continue

        return None

    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    async def start_login(self, db: Session, login_request: LoginRequest) -> dict:
        """Start the login process by sending verification code"""
        try:
            # Validate input
            if not validate_api_credentials(login_request.api_id, login_request.api_hash):
                raise Exception("Invalid API credentials format")

            # Normalize phone number
            normalized_phone = normalize_phone_number(login_request.phone_number)

            # Send verification code
            await telegram_service.send_code_request(
                login_request.api_id, login_request.api_hash, normalized_phone
            )

            return {
                "message": "Verification code sent to your phone",
                "phone_number": normalized_phone,
                "requires_code": True,
            }

        except Exception as e:
            raise Exception(f"Failed to start login: {str(e)}")

    async def verify_code(self, db: Session, verify_request: VerifyCodeRequest) -> dict:
        """Verify the authentication code"""
        try:
            normalized_phone = normalize_phone_number(verify_request.phone_number)

            # Verify code with Telegram
            success, needs_2fa = await telegram_service.verify_code(
                normalized_phone, verify_request.code
            )

            if not success:
                raise Exception("Code verification failed")

            if needs_2fa:
                return {
                    "message": "2FA password required",
                    "phone_number": normalized_phone,
                    "requires_2fa": True,
                }
            else:
                # Complete authentication
                return await self._complete_authentication(db, normalized_phone)

        except Exception as e:
            raise Exception(f"Failed to verify code: {str(e)}")

    async def verify_2fa(self, db: Session, verify_request: Verify2FARequest) -> dict:
        """Verify 2FA password"""
        try:
            normalized_phone = normalize_phone_number(verify_request.phone_number)

            # Verify 2FA with Telegram
            success = await telegram_service.verify_2fa(normalized_phone, verify_request.password)

            if not success:
                raise Exception("2FA verification failed")

            # Complete authentication
            return await self._complete_authentication(db, normalized_phone)

        except Exception as e:
            raise Exception(f"Failed to verify 2FA: {str(e)}")

    async def _complete_authentication(self, db: Session, phone_number: str) -> dict:
        """Complete the authentication process"""
        try:
            # Get session data from Telegram service
            session_data = await telegram_service.finalize_auth(phone_number)

            # Check if user exists
            user = self.get_user_by_phone(db, phone_number)

            if user:
                # Update existing user's session
                user.session_data = session_data
                user.updated_at = datetime.utcnow()
            else:
                # Create new user (this shouldn't happen in normal flow, but handle it)
                raise Exception("User not found. Please complete registration first.")

            db.commit()
            db.refresh(user)

            # Create access token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self.create_access_token(
                data={"sub": str(user.id), "phone": phone_number},
                expires_delta=access_token_expires,
            )

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "phone_number": phone_number,
                    "created_at": user.created_at,
                },
            }

        except Exception as e:
            raise Exception(f"Failed to complete authentication: {str(e)}")

    async def register_user(
        self, db: Session, api_id: str, api_hash: str, phone_number: str
    ) -> User:
        """Register a new user (called during first login)"""
        try:
            # Encrypt sensitive data
            encrypted_api_id = encryption_manager.encrypt(api_id)
            encrypted_api_hash = encryption_manager.encrypt(api_hash)
            encrypted_phone = encryption_manager.encrypt(normalize_phone_number(phone_number))

            # Create user
            user = User(
                api_id=encrypted_api_id, api_hash=encrypted_api_hash, phone_number=encrypted_phone
            )

            db.add(user)
            db.commit()
            db.refresh(user)

            # Create default settings
            settings = Settings(user_id=user.id)
            db.add(settings)
            db.commit()

            return user

        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to register user: {str(e)}")

    async def logout(self, db: Session, user_id: int):
        """Logout user and disconnect Telegram client"""
        try:
            # Disconnect Telegram client
            await telegram_service.disconnect_client(user_id)

            # Optionally clear session data from database
            user = self.get_user_by_id(db, user_id)
            if user:
                user.session_data = None
                user.updated_at = datetime.utcnow()
                db.commit()

        except Exception as e:
            raise Exception(f"Failed to logout: {str(e)}")

    async def get_auth_status(self, db: Session, user_id: int) -> dict:
        """Get authentication status for user"""
        try:
            user = self.get_user_by_id(db, user_id)
            if not user or not user.session_data:
                return {"authenticated": False}

            # Check if Telegram client is connected
            client = await telegram_service.get_client(user_id)
            if not client:
                # Try to create client from session
                decrypted_api_id = encryption_manager.decrypt(user.api_id)
                decrypted_api_hash = encryption_manager.decrypt(user.api_hash)

                await telegram_service.create_client(
                    user_id, decrypted_api_id, decrypted_api_hash, user.session_data
                )
                client = await telegram_service.get_client(user_id)

            if client:
                # Get user info from Telegram
                user_info = await telegram_service.get_me(client)
                return {"authenticated": True, "user_info": user_info}
            else:
                return {"authenticated": False}

        except Exception as e:
            return {"authenticated": False, "error": str(e)}


# Global instance
auth_service = AuthService()
