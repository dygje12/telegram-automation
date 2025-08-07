"""
Logging configuration and utilities
"""

import json
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging
    """

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "exc_info",
                "exc_text",
                "stack_info",
            ]:
                log_entry[key] = value

        return json.dumps(log_entry)


class ContextFilter(logging.Filter):
    """
    Filter to add context information to log records
    """

    def filter(self, record):
        # Add request ID if available (can be set by middleware)
        if not hasattr(record, "request_id"):
            record.request_id = getattr(self, "request_id", "N/A")

        # Add user ID if available
        if not hasattr(record, "user_id"):
            record.user_id = getattr(self, "user_id", "N/A")

        return True


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    json_format: bool = False,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> None:
    """
    Setup application logging configuration
    """

    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Create formatters
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)

    # Add context filter
    context_filter = ContextFilter()
    console_handler.addFilter(context_filter)

    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(detailed_formatter if not json_format else formatter)
        file_handler.addFilter(context_filter)

        root_logger.addHandler(file_handler)

    # Configure specific loggers
    configure_third_party_loggers(numeric_level)

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {log_level}, File: {log_file or 'None'}")


def configure_third_party_loggers(level: int) -> None:
    """
    Configure third-party library loggers
    """

    # Uvicorn loggers
    logging.getLogger("uvicorn").setLevel(level)
    logging.getLogger("uvicorn.error").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)  # Reduce noise

    # SQLAlchemy loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.dialects").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)

    # Telethon loggers
    logging.getLogger("telethon").setLevel(logging.WARNING)

    # APScheduler loggers
    logging.getLogger("apscheduler").setLevel(logging.WARNING)

    # Reduce noise from other libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name
    """
    return logging.getLogger(name)


class LoggerMixin:
    """
    Mixin class to add logging capabilities to any class
    """

    @property
    def logger(self) -> logging.Logger:
        return logging.getLogger(self.__class__.__name__)


def log_function_call(func):
    """
    Decorator to log function calls
    """

    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")

        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed with error: {str(e)}")
            raise

    return wrapper


def log_execution_time(func):
    """
    Decorator to log function execution time
    """
    import time

    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.4f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.4f} seconds: {str(e)}")
            raise

    return wrapper


class SecurityLogger:
    """
    Specialized logger for security events
    """

    def __init__(self):
        self.logger = logging.getLogger("security")

    def log_login_attempt(self, user_id: str, success: bool, ip_address: str = None):
        """Log login attempt"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"Login {status} - User: {user_id}, IP: {ip_address}")

    def log_permission_denied(self, user_id: str, resource: str, ip_address: str = None):
        """Log permission denied"""
        self.logger.warning(
            f"Permission denied - User: {user_id}, Resource: {resource}, IP: {ip_address}"
        )

    def log_rate_limit_exceeded(self, client_id: str, endpoint: str):
        """Log rate limit exceeded"""
        self.logger.warning(f"Rate limit exceeded - Client: {client_id}, Endpoint: {endpoint}")

    def log_suspicious_activity(
        self, description: str, user_id: str = None, ip_address: str = None
    ):
        """Log suspicious activity"""
        self.logger.error(f"Suspicious activity - {description}, User: {user_id}, IP: {ip_address}")


# Global security logger instance
security_logger = SecurityLogger()
