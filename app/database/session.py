from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.database.base import Base

engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    # echo=True, but we don't have env yet. Let's set echo=False for production, but we can set from app.core.config
    # We'll add a DEBUG flag later. For now, echo=False.
    echo=False,
    future=True,
)

# async session
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Dependency
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session