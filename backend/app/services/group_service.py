from sqlalchemy.orm import Session
from app.models import Group, User
from app.schemas import GroupCreate
from app.utils.validators import parse_group_input, sanitize_input
from app.services.telegram_service import telegram_service
from typing import List, Optional
from datetime import datetime

class GroupService:
    def __init__(self):
        pass
    
    def get_groups(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Group]:
        """Get all groups for a user"""
        return db.query(Group).filter(
            Group.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    def get_active_groups(self, db: Session, user_id: int) -> List[Group]:
        """Get only active groups for a user"""
        return db.query(Group).filter(
            Group.user_id == user_id,
            Group.is_active == True
        ).all()
    
    def get_group_by_id(self, db: Session, group_id: int, user_id: int) -> Optional[Group]:
        """Get a specific group by ID for a user"""
        return db.query(Group).filter(
            Group.id == group_id,
            Group.user_id == user_id
        ).first()
    
    def get_group_by_telegram_id(self, db: Session, telegram_group_id: str, user_id: int) -> Optional[Group]:
        """Get group by Telegram group ID"""
        return db.query(Group).filter(
            Group.group_id == telegram_group_id,
            Group.user_id == user_id
        ).first()
    
    async def add_group(self, db: Session, group_data: GroupCreate, user_id: int) -> Group:
        """Add a new group with validation"""
        try:
            # Check if user exists
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise Exception("User not found")
            
            # Get Telegram client
            client = await telegram_service.get_client(user_id)
            if not client:
                raise Exception("Telegram client not available. Please login first.")
            
            # Parse group input
            parsed_group_id, username, invite_link = parse_group_input(group_data.group_input)
            
            # Resolve group information from Telegram
            try:
                telegram_group_id, group_name, resolved_username = await telegram_service.resolve_group(
                    client, group_data.group_input
                )
            except Exception as e:
                raise Exception(f"Failed to resolve group: {str(e)}")
            
            # Check if group already exists
            existing_group = self.get_group_by_telegram_id(db, telegram_group_id, user_id)
            if existing_group:
                if existing_group.is_active:
                    raise Exception("Group already exists and is active")
                else:
                    # Reactivate existing group
                    existing_group.is_active = True
                    existing_group.group_name = group_name
                    existing_group.username = resolved_username
                    existing_group.updated_at = datetime.utcnow()
                    db.commit()
                    db.refresh(existing_group)
                    return existing_group
            
            # Test group access
            can_access = await telegram_service.test_group_access(client, telegram_group_id)
            if not can_access:
                raise Exception("Cannot access this group. Check permissions.")
            
            # Create new group
            group = Group(
                user_id=user_id,
                group_id=telegram_group_id,
                group_name=sanitize_input(group_name) if group_name else None,
                username=resolved_username,
                invite_link=invite_link if invite_link else None,
                is_active=True
            )
            
            db.add(group)
            db.commit()
            db.refresh(group)
            
            return group
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to add group: {str(e)}")
    
    def remove_group(self, db: Session, group_id: int, user_id: int) -> bool:
        """Remove a group (soft delete by setting is_active to False)"""
        try:
            group = self.get_group_by_id(db, group_id, user_id)
            if not group:
                raise Exception("Group not found")
            
            group.is_active = False
            group.updated_at = datetime.utcnow()
            
            db.commit()
            
            return True
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to remove group: {str(e)}")
    
    def delete_group(self, db: Session, group_id: int, user_id: int) -> bool:
        """Permanently delete a group"""
        try:
            group = self.get_group_by_id(db, group_id, user_id)
            if not group:
                raise Exception("Group not found")
            
            db.delete(group)
            db.commit()
            
            return True
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to delete group: {str(e)}")
    
    def toggle_group_status(self, db: Session, group_id: int, user_id: int) -> Optional[Group]:
        """Toggle group active status"""
        try:
            group = self.get_group_by_id(db, group_id, user_id)
            if not group:
                raise Exception("Group not found")
            
            group.is_active = not group.is_active
            group.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(group)
            
            return group
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to toggle group status: {str(e)}")
    
    async def validate_group(self, db: Session, group_id: int, user_id: int) -> dict:
        """Validate group access and update information"""
        try:
            group = self.get_group_by_id(db, group_id, user_id)
            if not group:
                raise Exception("Group not found")
            
            # Get Telegram client
            client = await telegram_service.get_client(user_id)
            if not client:
                raise Exception("Telegram client not available. Please login first.")
            
            # Test access
            can_access = await telegram_service.test_group_access(client, group.group_id)
            
            if can_access:
                # Update group information
                try:
                    telegram_group_id, group_name, username = await telegram_service.resolve_group(
                        client, group.group_id
                    )
                    
                    group.group_name = sanitize_input(group_name) if group_name else group.group_name
                    group.username = username
                    group.updated_at = datetime.utcnow()
                    db.commit()
                    
                except Exception:
                    pass  # Keep existing data if update fails
            
            return {
                "group_id": group.id,
                "telegram_group_id": group.group_id,
                "accessible": can_access,
                "group_name": group.group_name,
                "username": group.username
            }
            
        except Exception as e:
            raise Exception(f"Failed to validate group: {str(e)}")
    
    async def validate_all_groups(self, db: Session, user_id: int) -> dict:
        """Validate all active groups for a user"""
        try:
            groups = self.get_active_groups(db, user_id)
            results = {
                "total": len(groups),
                "accessible": 0,
                "inaccessible": 0,
                "groups": []
            }
            
            for group in groups:
                try:
                    validation_result = await self.validate_group(db, group.id, user_id)
                    results["groups"].append(validation_result)
                    
                    if validation_result["accessible"]:
                        results["accessible"] += 1
                    else:
                        results["inaccessible"] += 1
                        
                except Exception as e:
                    results["groups"].append({
                        "group_id": group.id,
                        "telegram_group_id": group.group_id,
                        "accessible": False,
                        "error": str(e)
                    })
                    results["inaccessible"] += 1
            
            return results
            
        except Exception as e:
            raise Exception(f"Failed to validate groups: {str(e)}")
    
    def get_group_count(self, db: Session, user_id: int) -> dict:
        """Get group statistics"""
        total = db.query(Group).filter(Group.user_id == user_id).count()
        active = db.query(Group).filter(
            Group.user_id == user_id,
            Group.is_active == True
        ).count()
        inactive = total - active
        
        return {
            "total": total,
            "active": active,
            "inactive": inactive
        }
    
    def search_groups(self, db: Session, user_id: int, query: str) -> List[Group]:
        """Search groups by name or username"""
        if not query or len(query.strip()) == 0:
            return []
        
        search_term = f"%{query.strip()}%"
        
        return db.query(Group).filter(
            Group.user_id == user_id,
            Group.is_active == True,
            (Group.group_name.ilike(search_term) | 
             Group.username.ilike(search_term))
        ).all()

# Global instance
group_service = GroupService()

