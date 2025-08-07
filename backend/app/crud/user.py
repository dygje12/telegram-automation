"""
CRUD operations for User model
"""

from typing import List, Optional

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.database import User
from app.models.schemas import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    CRUD operations for User model with authentication methods
    """

    def get_by_phone(self, db: Session, *, phone_number: str) -> Optional[User]:
        """
        Get user by phone number
        """
        return db.query(User).filter(User.phone_number == phone_number).first()

    def get_by_telegram_id(self, db: Session, *, telegram_id: int) -> Optional[User]:
        """
        Get user by Telegram ID
        """
        return db.query(User).filter(User.telegram_id == telegram_id).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Create user with hashed password
        """
        create_data = obj_in.dict()
        create_data.pop("password")

        db_obj = User(**create_data, hashed_password=get_password_hash(obj_in.password))

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_password(self, db: Session, *, db_obj: User, new_password: str) -> User:
        """
        Update user password
        """
        db_obj.hashed_password = get_password_hash(new_password)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, phone_number: str, password: str) -> Optional[User]:
        """
        Authenticate user by phone number and password
        """
        user = self.get_by_phone(db, phone_number=phone_number)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        """
        Check if user is active
        """
        return user.is_active

    def is_telegram_authenticated(self, user: User) -> bool:
        """
        Check if user has authenticated with Telegram
        """
        return user.telegram_id is not None and user.telegram_session is not None

    def get_active_users(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all active users
        """
        return db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()

    def get_telegram_authenticated_users(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """
        Get users who have authenticated with Telegram
        """
        return (
            db.query(User)
            .filter(
                and_(
                    User.is_active == True,
                    User.telegram_id.isnot(None),
                    User.telegram_session.isnot(None),
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_users(
        self, db: Session, *, query: str, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """
        Search users by name or phone number
        """
        search_filter = or_(
            User.first_name.like(f"%{query}%"),
            User.last_name.like(f"%{query}%"),
            User.phone_number.like(f"%{query}%"),
        )

        return db.query(User).filter(search_filter).offset(skip).limit(limit).all()

    def update_telegram_session(
        self, db: Session, *, user: User, telegram_id: int, session_data: str
    ) -> User:
        """
        Update user's Telegram session data
        """
        user.telegram_id = telegram_id
        user.telegram_session = session_data
        user.telegram_authenticated_at = db.execute("SELECT CURRENT_TIMESTAMP").scalar()

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def clear_telegram_session(self, db: Session, *, user: User) -> User:
        """
        Clear user's Telegram session data
        """
        user.telegram_id = None
        user.telegram_session = None
        user.telegram_authenticated_at = None

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_users_with_stats(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get users with message sending statistics
        """
        # This would require joins with message/schedule tables
        # Implementation depends on the actual database schema
        return db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()


# Create instance
user = CRUDUser(User)
