from datetime import timedelta
from jose import JWTError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.database.session import get_db
from app.schemas.user import UserCreate, Token
from app.services.auth_service import authenticate_user, register_user

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    user = await register_user(db, user_in)
    access_token = create_access_token(subject=user.email)
    refresh_token = create_refresh_token(subject=user.email)
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
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

@router.post("/refresh", response_model=Token)
async def refresh_token_endpoint(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    # Decode the refresh token to get the user email
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Optionally, check if the user still exists and is active
    # For simplicity, we just generate new tokens
    access_token = create_access_token(subject=email)
    new_refresh_token = create_refresh_token(subject=email)
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )