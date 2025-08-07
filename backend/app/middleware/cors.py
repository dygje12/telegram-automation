"""
CORS Middleware Configuration
Provides secure CORS configuration for production environment
"""

import os
from typing import List

from fastapi.middleware.cors import CORSMiddleware


def get_allowed_origins() -> List[str]:
    """
    Get allowed origins from environment variables
    In production, this should be specific domains only
    """
    origins_env = os.getenv("ALLOWED_ORIGINS", "")

    if origins_env:
        # Parse comma-separated origins from environment
        origins = [origin.strip() for origin in origins_env.split(",")]
        return origins

    # Development fallback - should not be used in production
    if os.getenv("ENVIRONMENT", "development") == "development":
        return [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ]

    # Production default - empty list means no CORS
    return []


def configure_cors_middleware(app):
    """
    Configure CORS middleware with secure settings
    """
    allowed_origins = get_allowed_origins()

    # Only add CORS middleware if origins are specified
    if allowed_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=[
                "Accept",
                "Accept-Language",
                "Content-Language",
                "Content-Type",
                "Authorization",
                "X-Requested-With",
            ],
            expose_headers=["X-Total-Count"],
            max_age=600,  # Cache preflight requests for 10 minutes
        )

        return True

    return False
