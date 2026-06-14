import time
import logging
from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 120, window: int = 60):
        """
        Sliding window rate limiter middleware.
        Defaults: 120 requests per minute per client IP.
        """
        super().__init__(app)
        self.limit = limit
        self.window = window
        self.requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        
        # Bypass health-check routes
        if request.url.path in ["/api/health", "/"]:
            return await call_next(request)
            
        now = time.time()
        
        # Clean timestamps outside the sliding window
        self.requests[client_ip] = [t for t in self.requests[client_ip] if now - t < self.window]
        
        if len(self.requests[client_ip]) >= self.limit:
            logger.warning(f"Rate limit exceeded for client IP: {client_ip} on path {request.url.path}")
            return Response(
                content='{"detail": "Too many requests. Please slow down."}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json"
            )
            
        self.requests[client_ip].append(now)
        return await call_next(request)
