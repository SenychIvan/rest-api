import os
import time
from typing import Optional

import redis.asyncio as redis
from fastapi import Request
from fastapi.responses import JSONResponse
from jose import JWTError, jwt

from app.core.security import SECRET_KEY, ALGORITHM


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

AUTH_LIMIT = 10
ANON_LIMIT = 2
WINDOW_SECONDS = 60

redis_client = redis.from_url(REDIS_URL, decode_responses=True)


def get_username_from_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload.get("sub")
    except JWTError:
        return None


def get_client_identity(request: Request) -> tuple[str, int]:
    auth_header = request.headers.get("Authorization")

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        username = get_username_from_token(token)

        if username:
            return f"user:{username}", AUTH_LIMIT

    client_ip = request.client.host if request.client else "unknown"
    return f"anon:{client_ip}", ANON_LIMIT


async def rate_limit_middleware(request: Request, call_next):
    if request.url.path in ["/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)

    identity, limit = get_client_identity(request)
    current_window = int(time.time() // WINDOW_SECONDS)

    key = f"rate_limit:{identity}:{current_window}"

    current_count = await redis_client.incr(key)

    if current_count == 1:
        await redis_client.expire(key, WINDOW_SECONDS)

    if current_count > limit:
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Rate limit exceeded",
                "limit": limit,
                "window_seconds": WINDOW_SECONDS,
            },
        )

    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(limit)
    response.headers["X-RateLimit-Remaining"] = str(max(limit - current_count, 0))

    return response