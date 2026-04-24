from fastapi import APIRouter, HTTPException, status

from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])

FAKE_USER = {
    "username": "admin",
    "password": "admin123",
}


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    if payload.username != FAKE_USER["username"] or payload.password != FAKE_USER["password"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    return TokenResponse(
        access_token=create_access_token(payload.username),
        refresh_token=create_refresh_token(payload.username),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest):
    username = verify_token(payload.refresh_token, expected_type="refresh")

    return TokenResponse(
        access_token=create_access_token(username),
        refresh_token=create_refresh_token(username),
    )