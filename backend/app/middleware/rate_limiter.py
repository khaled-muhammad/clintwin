"""
Rate Limiter Middleware
=======================
Simple in-memory rate limiting with configurable limits per endpoint.
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple
from collections import defaultdict
import time
import asyncio
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    In-memory rate limiter using sliding window algorithm.
    
    For production, replace with Redis-based implementation.
    """
    
    def __init__(self):
        # Store: {client_key: [(timestamp, count), ...]}
        self._requests: Dict[str, list] = defaultdict(list)
        self._lock = asyncio.Lock()
        
        # Default rate limits: (max_requests, window_seconds)
        self.default_limit = (100, 60)  # 100 requests per minute
        
        # Endpoint-specific limits
        self.endpoint_limits = {
            "/api/akinator/start": (20, 60),      # 20 sessions per minute
            "/api/akinator/answer": (60, 60),     # 60 answers per minute
            "/api/image/upload": (10, 60),        # 10 uploads per minute
            "/api/image/identify-base64": (10, 60),
            "/api/interactions/check": (30, 60),  # 30 checks per minute
        }
    
    def _get_client_key(self, request: Request) -> str:
        """Get unique client identifier."""
        # Use X-Forwarded-For if behind proxy, otherwise use client host
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        return f"{client_ip}:{request.url.path}"
    
    def _get_limit_for_path(self, path: str) -> Tuple[int, int]:
        """Get rate limit for specific path."""
        # Check exact match
        if path in self.endpoint_limits:
            return self.endpoint_limits[path]
        
        # Check prefix match
        for endpoint, limit in self.endpoint_limits.items():
            if path.startswith(endpoint.rsplit("/", 1)[0]):
                return limit
        
        return self.default_limit
    
    async def is_allowed(self, request: Request) -> Tuple[bool, int]:
        """
        Check if request is allowed under rate limit.
        
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        async with self._lock:
            client_key = self._get_client_key(request)
            max_requests, window_seconds = self._get_limit_for_path(request.url.path)
            
            now = time.time()
            window_start = now - window_seconds
            
            # Clean old entries
            self._requests[client_key] = [
                ts for ts in self._requests[client_key]
                if ts > window_start
            ]
            
            # Check limit
            if len(self._requests[client_key]) >= max_requests:
                # Calculate retry after
                oldest = min(self._requests[client_key]) if self._requests[client_key] else now
                retry_after = int(oldest + window_seconds - now) + 1
                return False, max(1, retry_after)
            
            # Record this request
            self._requests[client_key].append(now)
            return True, 0
    
    async def cleanup(self):
        """Periodic cleanup of old entries."""
        async with self._lock:
            now = time.time()
            keys_to_delete = []
            
            for key, timestamps in self._requests.items():
                # Remove entries older than 5 minutes
                self._requests[key] = [ts for ts in timestamps if now - ts < 300]
                if not self._requests[key]:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self._requests[key]


# Global rate limiter instance
_rate_limiter = None


def get_rate_limiter() -> RateLimiter:
    """Get or create rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware.
    
    Returns 429 Too Many Requests when limit exceeded.
    """
    
    # Paths to skip rate limiting
    SKIP_PATHS = {"/", "/health", "/docs", "/openapi.json", "/redoc"}
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for certain paths
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)
        
        limiter = get_rate_limiter()
        is_allowed, retry_after = await limiter.is_allowed(request)
        
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for {request.client.host}: {request.url.path}")
            
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "message": f"Too many requests. Please try again in {retry_after} seconds.",
                    "message_ar": f"طلبات كثيرة جداً. يرجى المحاولة مرة أخرى بعد {retry_after} ثانية.",
                    "retry_after": retry_after
                },
                headers={"Retry-After": str(retry_after)}
            )
        
        return await call_next(request)
