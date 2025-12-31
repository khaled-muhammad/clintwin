"""
Request Logging Middleware
==========================
Comprehensive request/response logging with timing and correlation IDs.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import time
import uuid
import logging

logger = logging.getLogger("clintwin.requests")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Request logging middleware.
    
    Logs:
    - Request method, path, and client IP
    - Response status and timing
    - Correlation IDs for request tracing
    """
    
    # Paths to skip detailed logging
    SKIP_PATHS = {"/health", "/docs", "/openapi.json", "/redoc", "/favicon.ico"}
    
    async def dispatch(self, request: Request, call_next):
        # Skip logging for certain paths
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)
        
        # Generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())[:8]
        
        # Get client info
        client_ip = self._get_client_ip(request)
        
        # Start timing
        start_time = time.time()
        
        # Log request
        logger.info(
            f"[{correlation_id}] --> {request.method} {request.url.path} "
            f"from {client_ip}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response
            log_level = logging.WARNING if response.status_code >= 400 else logging.INFO
            logger.log(
                log_level,
                f"[{correlation_id}] <-- {response.status_code} "
                f"({duration_ms:.1f}ms)"
            )
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Response-Time"] = f"{duration_ms:.1f}ms"
            
            return response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"[{correlation_id}] <-- ERROR after {duration_ms:.1f}ms: {str(e)}"
            )
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP, handling proxies."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"
