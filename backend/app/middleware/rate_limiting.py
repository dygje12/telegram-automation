"""
Rate Limiting Middleware
Implements rate limiting to prevent abuse and DoS attacks
"""

import asyncio
import logging
import time
from collections import defaultdict, deque
from typing import Deque, Dict

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter implementation
    """

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def is_allowed(self, client_id: str) -> bool:
        """
        Check if client is allowed to make a request
        """
        async with self._lock:
            now = time.time()
            client_requests = self.clients[client_id]

            # Remove old requests outside the window
            while client_requests and client_requests[0] <= now - self.window_seconds:
                client_requests.popleft()

            # Check if client has exceeded the limit
            if len(client_requests) >= self.max_requests:
                return False

            # Add current request
            client_requests.append(now)
            return True

    async def get_remaining_requests(self, client_id: str) -> int:
        """
        Get remaining requests for client
        """
        async with self._lock:
            now = time.time()
            client_requests = self.clients[client_id]

            # Remove old requests outside the window
            while client_requests and client_requests[0] <= now - self.window_seconds:
                client_requests.popleft()

            return max(0, self.max_requests - len(client_requests))

    async def get_reset_time(self, client_id: str) -> float:
        """
        Get time when rate limit resets for client
        """
        async with self._lock:
            client_requests = self.clients[client_id]
            if not client_requests:
                return time.time()

            return client_requests[0] + self.window_seconds


# Global rate limiters for different endpoints
rate_limiters = {
    "default": RateLimiter(max_requests=60, window_seconds=60),  # 60 requests per minute
    "auth": RateLimiter(max_requests=5, window_seconds=300),  # 5 requests per 5 minutes
    "messages": RateLimiter(max_requests=10, window_seconds=60),  # 10 requests per minute
    "scheduler": RateLimiter(max_requests=20, window_seconds=60),  # 20 requests per minute
}


def get_client_id(request: Request) -> str:
    """
    Get client identifier for rate limiting
    Uses IP address and User-Agent for better identification
    """
    # Get real IP address (considering proxies)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"

    # Include User-Agent for better client identification
    user_agent = request.headers.get("User-Agent", "")[:50]  # Limit length

    return f"{client_ip}:{hash(user_agent)}"


def get_rate_limiter_for_path(path: str) -> RateLimiter:
    """
    Get appropriate rate limiter based on request path
    """
    if path.startswith("/auth"):
        return rate_limiters["auth"]
    elif path.startswith("/messages"):
        return rate_limiters["messages"]
    elif path.startswith("/scheduler"):
        return rate_limiters["scheduler"]
    else:
        return rate_limiters["default"]


async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware
    """
    # Skip rate limiting for health checks and docs
    if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)

    client_id = get_client_id(request)
    rate_limiter = get_rate_limiter_for_path(request.url.path)

    try:
        # Check if request is allowed
        if not await rate_limiter.is_allowed(client_id):
            # Get rate limit info
            remaining = await rate_limiter.get_remaining_requests(client_id)
            reset_time = await rate_limiter.get_reset_time(client_id)

            logger.warning(f"Rate limit exceeded for client {client_id} on path {request.url.path}")

            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": int(reset_time - time.time()),
                    "limit": rate_limiter.max_requests,
                    "window": rate_limiter.window_seconds,
                },
                headers={
                    "X-RateLimit-Limit": str(rate_limiter.max_requests),
                    "X-RateLimit-Remaining": str(remaining),
                    "X-RateLimit-Reset": str(int(reset_time)),
                    "Retry-After": str(int(reset_time - time.time())),
                },
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        remaining = await rate_limiter.get_remaining_requests(client_id)
        reset_time = await rate_limiter.get_reset_time(client_id)

        response.headers["X-RateLimit-Limit"] = str(rate_limiter.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(reset_time))

        return response

    except Exception as e:
        logger.error(f"Rate limiting error: {str(e)}")
        # Continue processing if rate limiting fails
        return await call_next(request)
