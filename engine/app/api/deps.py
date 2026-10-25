# For: FastAPI route dependency injection and role-based access control
# Must never: Bypass role enforcement or token signature validation

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from engine.app.core.security import decode_access_token
from engine.app.db.connection import get_db
from engine.app.db.repo_auth import get_user_by_id

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Validates JWT bearer token and injects authenticated user profile."""
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHENTICATED", "message": "Invalid or expired session token."}
        )
    with get_db() as conn:
        user = get_user_by_id(conn, payload["sub"])
    if not user or not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHENTICATED", "message": "User account is inactive or disabled."}
        )
    return user


def require_role(allowed_roles: list[str]):
    """Decorator factory for role-based endpoint authorization."""
    def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": f"Action requires one of roles: {', '.join(allowed_roles)}"}
            )
        return current_user
    return role_checker
