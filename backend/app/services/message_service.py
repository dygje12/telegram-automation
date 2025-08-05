from sqlalchemy.orm import Session
from app.models import Message, User
from app.schemas import MessageCreate, MessageUpdate
from app.utils.validators import validate_message_content, sanitize_input
from typing import List, Optional
from datetime import datetime

class MessageService:
    def __init__(self):
        pass
    
    def get_messages(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Message]:
        """Get all messages for a user"""
        return db.query(Message).filter(
            Message.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    def get_active_messages(self, db: Session, user_id: int) -> List[Message]:
        """Get only active messages for a user"""
        return db.query(Message).filter(
            Message.user_id == user_id,
            Message.is_active == True
        ).all()
    
    def get_message_by_id(self, db: Session, message_id: int, user_id: int) -> Optional[Message]:
        """Get a specific message by ID for a user"""
        return db.query(Message).filter(
            Message.id == message_id,
            Message.user_id == user_id
        ).first()
    
    def create_message(self, db: Session, message_data: MessageCreate, user_id: int) -> Message:
        """Create a new message template"""
        try:
            # Validate content
            if not validate_message_content(message_data.content):
                raise Exception("Invalid message content")
            
            # Sanitize input
            title = sanitize_input(message_data.title)
            content = sanitize_input(message_data.content)
            
            if not title or len(title.strip()) == 0:
                raise Exception("Message title cannot be empty")
            
            # Check if user exists
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise Exception("User not found")
            
            # Create message
            message = Message(
                user_id=user_id,
                title=title,
                content=content,
                is_active=message_data.is_active
            )
            
            db.add(message)
            db.commit()
            db.refresh(message)
            
            return message
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to create message: {str(e)}")
    
    def update_message(self, db: Session, message_id: int, message_data: MessageUpdate, user_id: int) -> Optional[Message]:
        """Update an existing message"""
        try:
            # Get message
            message = self.get_message_by_id(db, message_id, user_id)
            if not message:
                raise Exception("Message not found")
            
            # Update fields
            if message_data.title is not None:
                title = sanitize_input(message_data.title)
                if not title or len(title.strip()) == 0:
                    raise Exception("Message title cannot be empty")
                message.title = title
            
            if message_data.content is not None:
                if not validate_message_content(message_data.content):
                    raise Exception("Invalid message content")
                content = sanitize_input(message_data.content)
                message.content = content
            
            if message_data.is_active is not None:
                message.is_active = message_data.is_active
            
            message.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(message)
            
            return message
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to update message: {str(e)}")
    
    def delete_message(self, db: Session, message_id: int, user_id: int) -> bool:
        """Delete a message"""
        try:
            message = self.get_message_by_id(db, message_id, user_id)
            if not message:
                raise Exception("Message not found")
            
            db.delete(message)
            db.commit()
            
            return True
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to delete message: {str(e)}")
    
    def toggle_message_status(self, db: Session, message_id: int, user_id: int) -> Optional[Message]:
        """Toggle message active status"""
        try:
            message = self.get_message_by_id(db, message_id, user_id)
            if not message:
                raise Exception("Message not found")
            
            message.is_active = not message.is_active
            message.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(message)
            
            return message
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to toggle message status: {str(e)}")
    
    def get_message_count(self, db: Session, user_id: int) -> dict:
        """Get message statistics"""
        total = db.query(Message).filter(Message.user_id == user_id).count()
        active = db.query(Message).filter(
            Message.user_id == user_id,
            Message.is_active == True
        ).count()
        inactive = total - active
        
        return {
            "total": total,
            "active": active,
            "inactive": inactive
        }
    
    def duplicate_message(self, db: Session, message_id: int, user_id: int) -> Optional[Message]:
        """Duplicate an existing message"""
        try:
            original = self.get_message_by_id(db, message_id, user_id)
            if not original:
                raise Exception("Message not found")
            
            # Create duplicate
            duplicate = Message(
                user_id=user_id,
                title=f"{original.title} (Copy)",
                content=original.content,
                is_active=False  # Start as inactive
            )
            
            db.add(duplicate)
            db.commit()
            db.refresh(duplicate)
            
            return duplicate
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to duplicate message: {str(e)}")

# Global instance
message_service = MessageService()

