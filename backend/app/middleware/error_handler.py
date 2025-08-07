"""
Global Error Handler Middleware
Provides secure error handling that doesn't leak sensitive information
"""

import logging
import os
import traceback
from typing import Union

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Custom exception for security-related errors"""

    pass


class BusinessLogicError(Exception):
    """Custom exception for business logic errors"""

    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


def is_development() -> bool:
    """Check if running in development environment"""
    return os.getenv("ENVIRONMENT", "production").lower() == "development"


def sanitize_error_message(error: Exception) -> str:
    """
    Sanitize error message to prevent information leakage
    """
    error_str = str(error)

    # Remove sensitive patterns
    sensitive_patterns = [
        "password",
        "token",
        "secret",
        "key",
        "api_key",
        "database",
        "connection",
        "file not found",
        "permission denied",
    ]

    error_lower = error_str.lower()
    for pattern in sensitive_patterns:
        if pattern in error_lower:
            return "Internal server error"

    return error_str


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions
    """
    logger.warning(f"HTTP {exc.status_code} error on {request.url.path}: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code, "success": False},
    )


async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle Starlette HTTP exceptions
    """
    logger.warning(f"Starlette HTTP {exc.status_code} error on {request.url.path}: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code, "success": False},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors
    """
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")

    # Format validation errors in a user-friendly way
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")

    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "details": errors,
            "status_code": 422,
            "success": False,
        },
    )


async def security_exception_handler(request: Request, exc: SecurityError):
    """
    Handle security-related errors
    """
    logger.error(f"Security error on {request.url.path}: {str(exc)}")

    return JSONResponse(
        status_code=403,
        content={
            "error": "Access denied",
            "message": "You don't have permission to access this resource",
            "status_code": 403,
            "success": False,
        },
    )


async def business_logic_exception_handler(request: Request, exc: BusinessLogicError):
    """
    Handle business logic errors
    """
    logger.info(f"Business logic error on {request.url.path}: {exc.message}")

    return JSONResponse(
        status_code=400,
        content={
            "error": exc.message,
            "error_code": exc.error_code,
            "status_code": 400,
            "success": False,
        },
    )


async def global_exception_handler(request: Request, exc: Exception):
    """
    Handle all other exceptions
    """
    # Log the full error for debugging
    logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}")

    if is_development():
        # In development, log the full traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

    # Sanitize error message for production
    if is_development():
        error_message = str(exc)
        include_traceback = True
    else:
        error_message = sanitize_error_message(exc)
        include_traceback = False

    response_content = {
        "error": "Internal server error",
        "message": error_message if is_development() else "An unexpected error occurred",
        "status_code": 500,
        "success": False,
    }

    if include_traceback:
        response_content["traceback"] = traceback.format_exc()

    return JSONResponse(status_code=500, content=response_content)


def setup_exception_handlers(app):
    """
    Setup all exception handlers for the FastAPI app
    """
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SecurityError, security_exception_handler)
    app.add_exception_handler(BusinessLogicError, business_logic_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
