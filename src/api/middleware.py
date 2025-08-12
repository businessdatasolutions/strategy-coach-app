"""
Middleware components for the AI Strategic Co-pilot API.

This module provides middleware for request validation, rate limiting,
error handling, and other cross-cutting concerns.
"""

import time
import logging
from typing import Dict, Optional
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.utils.config import get_config


logger = logging.getLogger(__name__)
config = get_config()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent API abuse.
    
    Implements a simple in-memory rate limiter with configurable
    requests per minute and per hour limits.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.requests_per_minute = config.rate_limit_requests_per_minute
        self.requests_per_hour = config.rate_limit_requests_per_hour
        
        # Track requests by IP
        self.minute_requests: Dict[str, list] = defaultdict(list)
        self.hour_requests: Dict[str, list] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Skip rate limiting for health checks and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limits
        current_time = time.time()
        
        # Clean old entries and check minute limit
        self._clean_old_requests(self.minute_requests, client_ip, 60)
        if len(self.minute_requests[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded (per minute) for IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute."
            )
        
        # Clean old entries and check hour limit
        self._clean_old_requests(self.hour_requests, client_ip, 3600)
        if len(self.hour_requests[client_ip]) >= self.requests_per_hour:
            logger.warning(f"Rate limit exceeded (per hour) for IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {self.requests_per_hour} requests per hour."
            )
        
        # Record request
        self.minute_requests[client_ip].append(current_time)
        self.hour_requests[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            self.requests_per_minute - len(self.minute_requests[client_ip])
        )
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(
            self.requests_per_hour - len(self.hour_requests[client_ip])
        )
        
        return response
    
    def _clean_old_requests(self, requests_dict: Dict[str, list], client_ip: str, window_seconds: int):
        """Remove requests older than the time window."""
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        if client_ip in requests_dict:
            requests_dict[client_ip] = [
                req_time for req_time in requests_dict[client_ip]
                if req_time > cutoff_time
            ]


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for validating incoming requests.
    
    Performs validation on request size, content type, and other
    security-related checks.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.max_request_size = 1024 * 1024  # 1MB max request size
    
    async def dispatch(self, request: Request, call_next):
        """Validate request before processing."""
        # Check Content-Length
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_request_size:
                    logger.warning(f"Request too large: {size} bytes from {request.client.host}")
                    raise HTTPException(
                        status_code=413,
                        detail=f"Request too large. Maximum size is {self.max_request_size} bytes."
                    )
            except ValueError:
                logger.warning(f"Invalid Content-Length header: {content_length}")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid Content-Length header"
                )
        
        # Validate JSON content type for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if not content_type.startswith("application/json") and request.url.path != "/docs":
                logger.warning(f"Invalid content type: {content_type} for {request.method} {request.url.path}")
                raise HTTPException(
                    status_code=415,
                    detail="Unsupported Media Type. Content-Type must be application/json"
                )
        
        # Process request
        response = await call_next(request)
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Enhanced error handling middleware.
    
    Provides consistent error responses and logging for all exceptions.
    """
    
    async def dispatch(self, request: Request, call_next):
        """Handle errors consistently."""
        try:
            response = await call_next(request)
            return response
            
        except HTTPException as exc:
            # Let FastAPI handle HTTP exceptions
            raise
            
        except Exception as exc:
            # Log unexpected errors
            logger.error(
                f"Unhandled exception in {request.method} {request.url.path}: {exc}",
                exc_info=True
            )
            
            # Return generic error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred",
                    "request_id": str(time.time()),
                    "path": str(request.url.path)
                }
            )


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Request/response logging middleware.
    
    Logs request details and response status for monitoring and debugging.
    """
    
    async def dispatch(self, request: Request, call_next):
        """Log request and response details."""
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Time: {process_time:.3f}s"
        )
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class SessionValidationMiddleware(BaseHTTPMiddleware):
    """
    Session validation middleware.
    
    Validates session IDs and ensures they follow the expected format.
    """
    
    async def dispatch(self, request: Request, call_next):
        """Validate session-related requests."""
        path = request.url.path
        
        # Check if this is a session-specific endpoint
        if "/conversation/" in path and "/message" in path:
            # Extract session ID from path
            parts = path.split("/")
            if "conversation" in parts:
                idx = parts.index("conversation")
                if idx + 1 < len(parts):
                    session_id = parts[idx + 1]
                    
                    # Validate session ID format (UUID)
                    import re
                    uuid_pattern = re.compile(
                        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
                        re.IGNORECASE
                    )
                    
                    if not uuid_pattern.match(session_id):
                        logger.warning(f"Invalid session ID format: {session_id}")
                        raise HTTPException(
                            status_code=400,
                            detail="Invalid session ID format. Must be a valid UUID."
                        )
        
        # Process request
        response = await call_next(request)
        return response