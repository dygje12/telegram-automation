"""
Application Configuration
Centralized configuration management with environment variable support
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with validation
    """

    # Application settings
    app_name: str = "Telegram Automation API"
    app_version: str = "1.0.0"
    environment: str = "production"
    debug: bool = False

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000

    # Database settings
    database_url: str = "sqlite:///./telegram_automation.db"

    # Security settings
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Telegram API settings
    telegram_api_id: Optional[int] = None
    telegram_api_hash: Optional[str] = None

    # CORS settings
    allowed_origins: str = ""

    # Rate limiting settings
    rate_limit_requests: int = 60
    rate_limit_window: int = 60

    # Logging settings
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # Scheduler settings
    scheduler_timezone: str = "UTC"
    max_concurrent_jobs: int = 10

    # Message sending settings
    default_delay_min: int = 30
    default_delay_max: int = 60
    max_retries: int = 3

    @validator("environment")
    def validate_environment(cls, v):
        allowed_envs = ["development", "staging", "production"]
        if v not in allowed_envs:
            raise ValueError(f"Environment must be one of {allowed_envs}")
        return v

    @validator("log_level")
    def validate_log_level(cls, v):
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of {allowed_levels}")
        return v.upper()

    @validator("secret_key")
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v

    @validator("allowed_origins")
    def validate_allowed_origins(cls, v):
        if v and not v.strip():
            return ""
        return v

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def allowed_origins_list(self) -> List[str]:
        if not self.allowed_origins:
            return []
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    """
    return Settings()


# Database configuration
def get_database_url() -> str:
    """
    Get database URL with proper configuration
    """
    settings = get_settings()

    # For SQLite, ensure the directory exists
    if settings.database_url.startswith("sqlite"):
        db_path = settings.database_url.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    return settings.database_url


# Logging configuration
def get_logging_config() -> dict:
    """
    Get logging configuration
    """
    settings = get_settings()

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.log_level,
                "formatter": "default",
                "stream": "ext://sys.stdout",
            }
        },
        "loggers": {
            "": {"level": settings.log_level, "handlers": ["console"], "propagate": False},
            "uvicorn": {"level": "INFO", "handlers": ["console"], "propagate": False},
            "uvicorn.error": {"level": "INFO", "handlers": ["console"], "propagate": False},
            "uvicorn.access": {"level": "INFO", "handlers": ["console"], "propagate": False},
        },
    }

    # Add file handler if log file is specified
    if settings.log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(settings.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": settings.log_level,
            "formatter": "detailed",
            "filename": settings.log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        }

        # Add file handler to all loggers
        for logger_config in config["loggers"].values():
            logger_config["handlers"].append("file")

    return config


# Security configuration
def get_security_config() -> dict:
    """
    Get security configuration
    """
    settings = get_settings()

    return {
        "secret_key": settings.secret_key,
        "algorithm": settings.algorithm,
        "access_token_expire_minutes": settings.access_token_expire_minutes,
        "password_min_length": 8,
        "password_require_uppercase": True,
        "password_require_lowercase": True,
        "password_require_numbers": True,
        "password_require_special": True,
    }
