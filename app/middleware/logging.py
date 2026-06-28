import time
import json
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = getattr(request.state, "request_id", "unknown")

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Get user ID if available (from auth)
        user_id = getattr(request.state, "user_id", None)

        response: Response = await call_next(request)
        process_time = (time.time() - start_time) * 1000

        # Create structured log entry
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "status_code": response.status_code,
            "execution_time_ms": round(process_time, 2),
            "client_ip": client_ip,
            "user_id": user_id,
            "user_agent": request.headers.get("user-agent", "unknown")
        }

        # Log as JSON for structured logging
        logger.info(json.dumps(log_entry))

        return response