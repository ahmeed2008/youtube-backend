from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
import time
from app.core.config import get_settings
from app.utils.logger import logger


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = None, window: int = None):
        super().__init__(app)
        settings = get_settings()
        self.requests_per_minute = requests_per_minute or settings.RATE_LIMIT_REQUESTS
        self.window = window or settings.RATE_LIMIT_WINDOW
        self.requests = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()
        
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < self.window
        ]
        
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Çok fazla istek. Lütfen bekleyin."
            )
        
        self.requests[client_ip].append(now)
        
        response = await call_next(request)
        return response
