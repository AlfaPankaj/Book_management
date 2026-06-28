from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Index, Boolean, Index, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database.base import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    genre = Column(String(100), nullable=True, index=True)
    published_year = Column(Integer, nullable=True)
    isbn = Column(String(17), unique=True, index=True, nullable=True)  # ISBN-13 with hyphens
    available = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Constraints
    __table_args__ = (
        CheckConstraint('published_year >= 1000 AND published_year <= 2030', name='check_published_year'),
        Index('idx_title_author', 'title', 'author'),
        Index('idx_genre_available', 'genre', 'available'),
    )