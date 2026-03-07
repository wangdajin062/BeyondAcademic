"""
Authentication API Router
Provides lightweight test authentication endpoints for local verification.
"""
from datetime import datetime, timedelta
import json
import os
import secrets
from typing import Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


def _load_test_accounts() -> Dict[str, str]:
    """
    Load test login accounts from TEST_LOGIN_ACCOUNTS env.

    Expected format:
        {"tester": "test123456", "researcher": "Research@2026"}
    """
    raw_accounts = os.getenv("TEST_LOGIN_ACCOUNTS", "")
    if not raw_accounts:
        return {
            "tester": "test123456",
            "researcher": "Research@2026",
        }

    try:
        accounts = json.loads(raw_accounts)
    except json.JSONDecodeError as exc:
        raise RuntimeError("TEST_LOGIN_ACCOUNTS must be valid JSON") from exc

    if not isinstance(accounts, dict) or not accounts:
        raise RuntimeError("TEST_LOGIN_ACCOUNTS must be a non-empty JSON object")

    normalized: Dict[str, str] = {}
    for username, password in accounts.items():
        if not isinstance(username, str) or not isinstance(password, str):
            raise RuntimeError("All TEST_LOGIN_ACCOUNTS entries must be string:string")
        normalized[username] = password

    return normalized


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=6, max_length=128)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: dict


@router.post("/test-login", response_model=LoginResponse)
async def test_login(payload: LoginRequest):
    if os.getenv("ENABLE_TEST_AUTH", "false").lower() != "true":
        raise HTTPException(status_code=403, detail="Test auth is disabled")

    test_accounts = _load_test_accounts()
    expected_password = test_accounts.get(payload.username)
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
