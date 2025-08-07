"""
Security utilities and authentication
"""

import logging
import os
import secrets
from datetime import datetime, timedelta
from typing import Any, Optional, Union

from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security scheme
security = HTTPBearer()


def get_secret_key() -> str:
    """
    Get or generate secret key for JWT
    """
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        # Generate a secure random key
        secret_key = secrets.token_urlsafe(32)
        logger.warning("No SECRET_KEY found in environment, using generated key")
    return secret_key


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    secret_key = get_secret_key()
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)

    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode JWT token
    """
    try:
        secret_key = get_secret_key()
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"JWT verification failed: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return None


def get_current_user_id(credentials: HTTPAuthorizationCredentials) -> str:
    """
    Extract user ID from JWT token
    """
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


def validate_password_strength(password: str) -> bool:
    """
    Validate password strength
    """
    if len(password) < 8:
        return False

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

    return has_upper and has_lower and has_digit and has_special


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a secure random token
    """
    return secrets.token_urlsafe(length)


def sanitize_input(input_str: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection attacks
    """
    if not isinstance(input_str, str):
        return ""

    # Remove null bytes
    sanitized = input_str.replace("\x00", "")

    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    # Remove potentially dangerous characters
    dangerous_chars = ["<", ">", '"', "'", "&", "\r", "\n"]
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")

    return sanitized.strip()


def is_safe_url(url: str) -> bool:
    """
    Check if URL is safe (basic validation)
    """
    if not url:
        return False

    # Check for common dangerous patterns
    dangerous_patterns = [
        "javascript:",
        "data:",
        "vbscript:",
        "file:",
        "ftp:",
    ]

    url_lower = url.lower()
    for pattern in dangerous_patterns:
        if pattern in url_lower:
            return False

    # Must start with http or https
    return url_lower.startswith(("http://", "https://"))


class SecurityHeaders:
    """
    Security headers for HTTP responses
    """

    @staticmethod
    def get_security_headers() -> dict:
        """
        Get recommended security headers
        """
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }
