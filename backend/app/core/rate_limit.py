from typing import Callable, Dict
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class RateLimiter:
    def __init__(self, requests: int, window: int):
        """
        Initialize rate limiter.
        
        Args:
            requests: Maximum number of requests allowed in the window
            window: Time window in seconds
        """
        self.requests = requests
        self.window = window
        self.clients: Dict[str, list] = {}
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if client is allowed to make a request."""
        now = datetime.now()
        
        # Remove old requests
        if client_id in self.clients:
            self.clients[client_id] = [
                timestamp for timestamp in self.clients[client_id]
                if timestamp > now - timedelta(seconds=self.window)
            ]
        else:
            self.clients[client_id] = []
        
        # Check if client has exceeded rate limit
        if len(self.clients[client_id]) >= self.requests:
            return False
        
        # Add new request
        self.clients[client_id].append(now)
        return True


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 60,
        exclude_paths: list = None
    ):
        """
        Initialize rate limit middleware.
        
        Args:
            app: The ASGI application
            requests_per_minute: Maximum number of requests allowed per minute
            exclude_paths: List of paths to exclude from rate limiting
        """
        super().__init__(app)
        self.limiter = RateLimiter(requests_per_minute, 60)
        self.exclude_paths = exclude_paths or []
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle incoming request."""
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Get client identifier (IP address or token)
        client_id = request.client.host
        if "Authorization" in request.headers:
            client_id = request.headers["Authorization"]
        
        # Check rate limit
        if not self.limiter.is_allowed(client_id):
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later."
                }
            )
        
        return await call_next(request)


def add_rate_limit(
    app: FastAPI,
    requests_per_minute: int = 60,
    exclude_paths: list = None
) -> None:
    """
    Add rate limiting middleware to FastAPI application.
    
    Args:
        app: FastAPI application instance
        requests_per_minute: Maximum number of requests allowed per minute
        exclude_paths: List of paths to exclude from rate limiting
    """
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=requests_per_minute,
        exclude_paths=exclude_paths
    ) 