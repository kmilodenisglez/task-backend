"""
Rate limiting utilities using in-memory storage
"""

import asyncio
import time
from collections import defaultdict, deque
from typing import Dict

from fastapi import HTTPException, Request

# Rate limiting middleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.logging import get_logger

logger = get_logger("rate_limiting")


class RateLimiter:
    """In-memory rate limiter using sliding window"""

    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.lock = asyncio.Lock()

    async def is_allowed(
        self, key: str, limit: int, window_seconds: int
    ) -> tuple[bool, Dict[str, int]]:
        """
        Check if request is allowed based on rate limit.

        Args:
            key: Unique identifier (e.g., IP address, user ID)
            limit: Maximum number of requests allowed
            window_seconds: Time window in seconds

        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        async with self.lock:
            now = time.time()
            window_start = now - window_seconds

            # Clean old requests
            requests = self.requests[key]
            while requests and requests[0] < window_start:
                requests.popleft()

            # Check if limit exceeded
            if len(requests) >= limit:
                reset_time = requests[0] + window_seconds
                return False, {
                    "limit": limit,
                    "remaining": 0,
                    "reset_time": reset_time,
                    "retry_after": int(reset_time - now),
                }

            # Add current request
            requests.append(now)

            return True, {
                "limit": limit,
                "remaining": limit - len(requests),
                "reset_time": now + window_seconds,
                "retry_after": 0,
            }


# Global rate limiter instance
rate_limiter = RateLimiter()


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    # Check for forwarded headers first
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fallback to direct client IP
    return request.client.host if request.client else "unknown"


async def check_rate_limit(
    request: Request,
    limit: int = 100,
    window_seconds: int = 3600,  # 1 hour
    key_prefix: str = "ip",
) -> None:
    """
    Check rate limit and raise exception if exceeded.

    Args:
        request: FastAPI request object
        limit: Maximum requests per window
        window_seconds: Time window in seconds
        key_prefix: Prefix for rate limit key
    """
    client_ip = get_client_ip(request)
    key = f"{key_prefix}:{client_ip}"

    is_allowed, rate_info = await rate_limiter.is_allowed(key, limit, window_seconds)

    if not is_allowed:
        logger.warning(
            "Rate limit exceeded",
            extra={
                "client_ip": client_ip,
                "endpoint": str(request.url.path),
                "rate_info": rate_info,
            },
        )

        raise HTTPException(
            status_code=429,
            detail={
                "message": "Rate limit exceeded",
                "retry_after": rate_info["retry_after"],
                "limit": rate_info["limit"],
            },
            headers={
                "X-RateLimit-Limit": str(rate_info["limit"]),
                "X-RateLimit-Remaining": str(rate_info["remaining"]),
                "X-RateLimit-Reset": str(int(rate_info["reset_time"])),
                "Retry-After": str(rate_info["retry_after"]),
            },
        )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for global rate limiting"""

    def __init__(self, app, calls: int = 100, period: int = 3600):
        super().__init__(app)
        self.calls = calls
        self.period = period

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path.startswith("/health"):
            return await call_next(request)

        await check_rate_limit(request, limit=self.calls, window_seconds=self.period)

        return await call_next(request)
