from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import limiter, rate_limit_exceeded_handler
from app.exceptions.handlers import add_exception_handlers
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import json

# Set up logging
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Add middleware
app.state.limiter = limiter
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(SlowAPIMiddleware)  # This adds the rate limiting middleware

# Rate limiter exception handler - using our custom handler
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Add custom exception handlers
add_exception_handlers(app)

app.include_router(api_router, prefix=settings.API_V1_STR)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/chat", response_class=HTMLResponse, tags=["ui"])
async def chat_interface():
    with open(os.path.join(static_dir, "index.html"), "r") as f:
        return f.read()

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}. Go to /chat to use the AI Assistant!"}

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}