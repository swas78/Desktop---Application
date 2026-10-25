# For: Authentication endpoints for user login, refresh, and session status
# Must never: Return cleartext passwords or bypass invalid credential counts

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from engine.app.core.security import verify_password, create_access_token
from engine.app.db.connection import get_db
from engine.app.db.repo_auth import (
    get_user_by_username, record_successful_login, record_failed_login
)
from engine.app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(payload: LoginRequest):
    """Authenticates username/password and returns JWT access and refresh tokens."""
    with get_db() as conn:
        user = get_user_by_username(conn, payload.username)
        if not user or not user["is_active"]:
            record_failed_login(conn, payload.username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "UNAUTHENTICATED", "message": "Invalid username or password."}
            )
        if user.get("locked_until"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "LOCKED", "message": "Account temporarily locked due to multiple failed attempts."}
            )
        if not verify_password(payload.password, user["password_hash"]):
            fails = record_failed_login(conn, payload.username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "UNAUTHENTICATED", "message": f"Invalid password. Failed attempts: {fails}"}
            )
        record_successful_login(conn, user["id"])
    
    access_token = create_access_token({"sub": user["id"], "role": user["role"]})
    refresh_token = create_access_token({"sub": user["id"], "type": "refresh"})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": 3600,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "name": user["full_name"],
            "role": user["role"]
        }
    }


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """Returns currently authenticated user profile."""
    return current_user
