from datetime import timedelta
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.repositories import user_repository as crud_user
from app.schemas.user import UserCreate, UserLogin, Token
from app.models.user import User

async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def register_user(db: AsyncSession, user_in: UserCreate) -> User:
    hashed_password = get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def login_user(db: AsyncSession, user_in: UserLogin) -> Token:
    user = await authenticate_user(db, user_in.email, user_in.password)
    if not user:
        raise ValueError("Incorrect email or password")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(subject=user.email)
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )

async def refresh_token(refresh_token: str) -> Token:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise ValueError("Invalid refresh token")
    email = payload.get("sub")
    if email is None:
        raise ValueError("Invalid refresh token")
    # In a real app, you might want to check the user still exists and is active
    # For simplicity, we just generate new tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(subject=email, expires_delta=access_token_expires)
    new_refresh_token = create_refresh_token(subject=email)
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )