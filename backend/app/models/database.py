from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Text, nullable=False)  # Encrypted
    api_hash = Column(Text, nullable=False)  # Encrypted
    phone_number = Column(Text, nullable=False)  # Encrypted
    session_data = Column(Text, nullable=True)  # Encrypted Telethon session
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    messages = relationship("Message", back_populates="user")
    groups = relationship("Group", back_populates="user")
    blacklist = relationship("Blacklist", back_populates="user")
    logs = relationship("Log", back_populates="user")
    settings = relationship("Settings", back_populates="user", uselist=False)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="messages")
    logs = relationship("Log", back_populates="message")


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(String(255), nullable=False)  # Telegram group ID
    group_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)  # @username
    invite_link = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="groups")


class Blacklist(Base):
    __tablename__ = "blacklist"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(String(255), nullable=False)
    blacklist_type = Column(String(50), nullable=False)  # 'temporary' or 'permanent'
    reason = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="blacklist")


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(String(255), nullable=False)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    status = Column(String(50), nullable=False)  # 'success', 'failed', 'blacklisted'
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="logs")
    message = relationship("Message", back_populates="logs")


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    min_interval = Column(Integer, default=4200)  # 1 hour 10 minutes in seconds
    max_interval = Column(Integer, default=5400)  # 1 hour 30 minutes in seconds
    min_delay = Column(Integer, default=5)  # 5 seconds
    max_delay = Column(Integer, default=10)  # 10 seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="settings")
