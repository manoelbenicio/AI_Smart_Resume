"""JWT authentication helpers and current-user dependency."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from smart_resume.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


class UserContext(BaseModel):
    """Authenticated user identity used by protected endpoints."""

    user_id: str
    email: str


def hash_password(plain: str) -> str:
    """Hash a plain password with bcrypt."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict[str, str], expires_minutes: int | None = None) -> str:
    """Create a signed JWT including expiration."""
    payload = data.copy()
    expire_delta = timedelta(minutes=expires_minutes or settings.jwt_expire_minutes)
    payload["exp"] = datetime.now(UTC) + expire_delta
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


async def get_current_user(token: str | None = Depends(oauth2_scheme)) -> UserContext:
    """Resolve current authenticated user from bearer token."""
    if not settings.auth_enabled:
        return UserContext(user_id="anonymous", email="local@dev")

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        email = payload.get("email")
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc

    if not user_id or not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    return UserContext(user_id=str(user_id), email=str(email))
