import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, validator


# Base schemas
class UserBase(BaseModel):
    api_id: str
    api_hash: str
    phone_number: str


class UserCreate(UserBase):
    pass


class UserResponse(BaseModel):
    id: int
    phone_number: str
    created_at: datetime

    class Config:
        from_attributes = True


# Authentication schemas
class LoginRequest(BaseModel):
    api_id: str
    api_hash: str
    phone_number: str

    @validator("phone_number")
    def validate_phone_number(cls, v):
        # Basic phone number validation
        if not re.match(r"^\+?[1-9]\d{1,14}$", v):
            raise ValueError("Invalid phone number format")
        return v


class VerifyCodeRequest(BaseModel):
    phone_number: str
    code: str


class Verify2FARequest(BaseModel):
    phone_number: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# Message schemas
class MessageBase(BaseModel):
    title: str
    content: str
    is_active: bool = True


class MessageCreate(MessageBase):
    pass


class MessageUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_active: Optional[bool] = None


class MessageResponse(MessageBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Group schemas
class GroupBase(BaseModel):
    group_input: str  # Can be link, ID, or username

    @validator("group_input")
    def validate_group_input(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Group input cannot be empty")
        return v.strip()


class GroupCreate(GroupBase):
    pass


class GroupResponse(BaseModel):
    id: int
    user_id: int
    group_id: str
    group_name: Optional[str]
    username: Optional[str]
    invite_link: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Blacklist schemas
class BlacklistResponse(BaseModel):
    id: int
    user_id: int
    group_id: str
    blacklist_type: str
    reason: Optional[str]
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Log schemas
class LogResponse(BaseModel):
    id: int
    user_id: int
    group_id: str
    message_id: Optional[int]
    status: str
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Settings schemas
class SettingsBase(BaseModel):
    min_interval: int = 4200
    max_interval: int = 5400
    min_delay: int = 5
    max_delay: int = 10

    @validator("min_interval", "max_interval")
    def validate_intervals(cls, v):
        if v < 60:  # Minimum 1 minute
            raise ValueError("Interval must be at least 60 seconds")
        if v > 86400:  # Maximum 24 hours
            raise ValueError("Interval cannot exceed 24 hours")
        return v

    @validator("min_delay", "max_delay")
    def validate_delays(cls, v):
        if v < 1:
            raise ValueError("Delay must be at least 1 second")
        if v > 300:  # Maximum 5 minutes
            raise ValueError("Delay cannot exceed 300 seconds")
        return v


class SettingsUpdate(SettingsBase):
    min_interval: Optional[int] = None
    max_interval: Optional[int] = None
    min_delay: Optional[int] = None
    max_delay: Optional[int] = None


class SettingsResponse(SettingsBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Scheduler schemas
class SchedulerStatus(BaseModel):
    is_running: bool
    next_run: Optional[datetime]
    last_run: Optional[datetime]
    total_messages_sent: int
    total_groups: int
    active_groups: int
    blacklisted_groups: int


# Generic response schemas
class MessageResponseGeneric(BaseModel):
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    message: str
    success: bool = False
    error_code: Optional[str] = None
