"""Authentication API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_resume.api.auth import create_access_token, hash_password, verify_password
from smart_resume.api.schemas import LoginRequest, RegisterRequest, RegisterResponse, TokenResponse
from smart_resume.db.engine import get_db
from smart_resume.db.models import UserRecord

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)) -> RegisterResponse:
    """Register a new user account."""
    email = request.email.strip().lower()
    exists = await db.scalar(select(UserRecord).where(UserRecord.email == email))
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = UserRecord(
        email=email,
        hashed_password=hash_password(request.password),
        full_name=request.full_name,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return RegisterResponse(user_id=user.id, email=user.email)


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Authenticate credentials and return JWT bearer token."""
    email = request.email.strip().lower()
    user = await db.scalar(select(UserRecord).where(UserRecord.email == email))
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({"sub": user.id, "email": user.email})
    return TokenResponse(access_token=token, token_type="bearer")
