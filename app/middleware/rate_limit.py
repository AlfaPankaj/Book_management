from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
import redis.asyncio as redis
import json

# Initialize Redis connection for rate limiting
redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

# Initialize limiter
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
)

# Custom rate limit exceeded handler
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": f"Rate limit exceeded: {exc.detail}"
            },
            "request_id": getattr(request.state, "request_id", None)
        },
        headers={
            "Retry-After": str(getattr(expr, "retry_after", 60)) if hasattr(expr, 'retry_after') else "60"
        }
    )

# RateLimitMiddleware is not used since we use SlowAPIMiddleware directly
class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        return response