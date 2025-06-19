from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import os
from typing import Optional, Callable

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Rate limit configuration
RATE_LIMIT_DEFAULT = "100/minute"  # Default rate limit
RATE_LIMIT_AUTH = "5/minute"       # Stricter limit for auth endpoints
RATE_LIMIT_API = "1000/hour"       # Higher limit for API endpoints

def get_rate_limit() -> str:
    """Get rate limit from environment variable or return default."""
    return os.getenv("RATE_LIMIT", RATE_LIMIT_DEFAULT)

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Custom handler for rate limit exceeded."""
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "detail": f"Too many requests. Please try again in {exc.retry_after} seconds.",
            "retry_after": exc.retry_after
        }
    )

def get_rate_limit_key(request: Request) -> str:
    """Get rate limit key based on request path."""
    path = request.url.path
    
    # Different rate limits for different endpoints
    if path.startswith("/auth"):
        return RATE_LIMIT_AUTH
    elif path.startswith("/api"):
        return RATE_LIMIT_API
    return get_rate_limit()

def rate_limit_middleware(app):
    """Rate limiting middleware factory."""
    
    # Add rate limit exceeded handler
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    
    # Use official SlowAPIMiddleware which handles request internally
    app.add_middleware(SlowAPIMiddleware)
    return app