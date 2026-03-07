"""
Authentication API Router
Provides lightweight test authentication endpoints for local verification.
"""
from datetime import datetime, timedelta
import secrets
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=6, max_length=128)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: dict


# Test credentials only for integration verification.
TEST_ACCOUNTS = {
    "tester": "test123456",
    "researcher": "Research@2026",
}


@router.post("/test-login", response_model=LoginResponse)
async def test_login(payload: LoginRequest):
    expected_password = TEST_ACCOUNTS.get(payload.username)
    if expected_password is None or expected_password != payload.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    expires_at = datetime.utcnow() + timedelta(hours=2)
    return LoginResponse(
        access_token=secrets.token_urlsafe(32),
        expires_at=expires_at,
        user={
            "username": payload.username,
            "display_name": payload.username.title(),
            "role": "tester",
        },
    )
