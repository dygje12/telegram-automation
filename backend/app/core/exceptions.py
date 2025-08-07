"""
Custom exceptions and error handling
"""

from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class TelegramAutomationException(Exception):
    """
    Base exception for Telegram Automation application
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(TelegramAutomationException):
    """
    Raised when input validation fails
    """

    pass


class AuthenticationError(TelegramAutomationException):
    """
    Raised when authentication fails
    """

    pass


class AuthorizationError(TelegramAutomationException):
    """
    Raised when user doesn't have permission
    """

    pass


class TelegramError(TelegramAutomationException):
    """
    Raised when Telegram API operations fail
    """

    pass


class DatabaseError(TelegramAutomationException):
    """
    Raised when database operations fail
    """

    pass


class ConfigurationError(TelegramAutomationException):
    """
    Raised when configuration is invalid
    """

    pass


class RateLimitError(TelegramAutomationException):
    """
    Raised when rate limit is exceeded
    """

    pass


class SchedulerError(TelegramAutomationException):
    """
    Raised when scheduler operations fail
    """

    pass


class MessageError(TelegramAutomationException):
    """
    Raised when message operations fail
    """

    pass


class GroupError(TelegramAutomationException):
    """
    Raised when group operations fail
    """

    pass


class BlacklistError(TelegramAutomationException):
    """
    Raised when blacklist operations fail
    """

    pass


# HTTP Exception mappings
def create_http_exception(
    status_code: int,
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> HTTPException:
    """
    Create HTTPException with structured error response
    """
    content = {"error": message, "success": False}

    if error_code:
        content["error_code"] = error_code

    if details:
        content["details"] = details

    return HTTPException(status_code=status_code, detail=content)


# Common HTTP exceptions
class HTTPExceptions:
    """
    Common HTTP exceptions with consistent structure
    """

    @staticmethod
    def bad_request(
        message: str = "Bad request", error_code: str = None, details: Dict[str, Any] = None
    ):
        return create_http_exception(status.HTTP_400_BAD_REQUEST, message, error_code, details)

    @staticmethod
    def unauthorized(
        message: str = "Unauthorized", error_code: str = None, details: Dict[str, Any] = None
    ):
        return create_http_exception(status.HTTP_401_UNAUTHORIZED, message, error_code, details)

    @staticmethod
    def forbidden(
        message: str = "Forbidden", error_code: str = None, details: Dict[str, Any] = None
    ):
        return create_http_exception(status.HTTP_403_FORBIDDEN, message, error_code, details)

    @staticmethod
    def not_found(
        message: str = "Not found", error_code: str = None, details: Dict[str, Any] = None
    ):
        return create_http_exception(status.HTTP_404_NOT_FOUND, message, error_code, details)

    @staticmethod
    def conflict(message: str = "Conflict", error_code: str = None, details: Dict[str, Any] = None):
        return create_http_exception(status.HTTP_409_CONFLICT, message, error_code, details)

    @staticmethod
    def unprocessable_entity(
        message: str = "Unprocessable entity",
        error_code: str = None,
        details: Dict[str, Any] = None,
    ):
        return create_http_exception(
            status.HTTP_422_UNPROCESSABLE_ENTITY, message, error_code, details
        )

    @staticmethod
    def too_many_requests(
        message: str = "Too many requests", error_code: str = None, details: Dict[str, Any] = None
    ):
        return create_http_exception(
            status.HTTP_429_TOO_MANY_REQUESTS, message, error_code, details
        )

    @staticmethod
    def internal_server_error(
        message: str = "Internal server error",
        error_code: str = None,
        details: Dict[str, Any] = None,
    ):
        return create_http_exception(
            status.HTTP_500_INTERNAL_SERVER_ERROR, message, error_code, details
        )

    @staticmethod
    def service_unavailable(
        message: str = "Service unavailable", error_code: str = None, details: Dict[str, Any] = None
    ):
        return create_http_exception(
            status.HTTP_503_SERVICE_UNAVAILABLE, message, error_code, details
        )


# Exception to HTTP status code mapping
EXCEPTION_STATUS_MAP = {
    ValidationError: status.HTTP_400_BAD_REQUEST,
    AuthenticationError: status.HTTP_401_UNAUTHORIZED,
    AuthorizationError: status.HTTP_403_FORBIDDEN,
    TelegramError: status.HTTP_400_BAD_REQUEST,
    DatabaseError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ConfigurationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    RateLimitError: status.HTTP_429_TOO_MANY_REQUESTS,
    SchedulerError: status.HTTP_400_BAD_REQUEST,
    MessageError: status.HTTP_400_BAD_REQUEST,
    GroupError: status.HTTP_400_BAD_REQUEST,
    BlacklistError: status.HTTP_400_BAD_REQUEST,
}


def exception_to_http_exception(exc: TelegramAutomationException) -> HTTPException:
    """
    Convert custom exception to HTTP exception
    """
    status_code = EXCEPTION_STATUS_MAP.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)

    return create_http_exception(
        status_code=status_code, message=exc.message, error_code=exc.error_code, details=exc.details
    )


# Error codes for different types of errors
class ErrorCodes:
    """
    Standardized error codes
    """

    # Authentication errors
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"

    # Authorization errors
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    ACCESS_DENIED = "ACCESS_DENIED"

    # Validation errors
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"

    # Telegram errors
    TELEGRAM_AUTH_FAILED = "TELEGRAM_AUTH_FAILED"
    TELEGRAM_API_ERROR = "TELEGRAM_API_ERROR"
    TELEGRAM_RATE_LIMIT = "TELEGRAM_RATE_LIMIT"
    TELEGRAM_FLOOD_WAIT = "TELEGRAM_FLOOD_WAIT"

    # Database errors
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATABASE_QUERY_ERROR = "DATABASE_QUERY_ERROR"
    RECORD_NOT_FOUND = "RECORD_NOT_FOUND"
    DUPLICATE_RECORD = "DUPLICATE_RECORD"

    # Scheduler errors
    SCHEDULER_NOT_RUNNING = "SCHEDULER_NOT_RUNNING"
    JOB_NOT_FOUND = "JOB_NOT_FOUND"
    INVALID_SCHEDULE = "INVALID_SCHEDULE"

    # Message errors
    MESSAGE_TOO_LONG = "MESSAGE_TOO_LONG"
    INVALID_MESSAGE_FORMAT = "INVALID_MESSAGE_FORMAT"
    MESSAGE_SEND_FAILED = "MESSAGE_SEND_FAILED"

    # Group errors
    GROUP_NOT_FOUND = "GROUP_NOT_FOUND"
    GROUP_ACCESS_DENIED = "GROUP_ACCESS_DENIED"
    INVALID_GROUP_ID = "INVALID_GROUP_ID"

    # Blacklist errors
    BLACKLIST_ENTRY_EXISTS = "BLACKLIST_ENTRY_EXISTS"
    BLACKLIST_ENTRY_NOT_FOUND = "BLACKLIST_ENTRY_NOT_FOUND"

    # Rate limiting errors
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # Configuration errors
    MISSING_CONFIGURATION = "MISSING_CONFIGURATION"
    INVALID_CONFIGURATION = "INVALID_CONFIGURATION"
