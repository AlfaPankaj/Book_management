from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, example="The Great Gatsby")
    author: str = Field(..., min_length=1, max_length=255, example="F. Scott Fitzgerald")
    genre: Optional[str] = Field(None, max_length=100, example="Fiction")
    published_year: Optional[int] = Field(None, ge=1000, le=2030, example=1925)
    isbn: Optional[str] = Field(None, max_length=17, example="9780743273565")  # ISBN-13 format
    available: bool = Field(True, description="Whether the book is available for checkout")

    @validator('isbn')
    def validate_isbn(cls, v):
        if v is None:
            return v
        # Remove hyphens and spaces for validation
        clean_isbn = re.sub(r'[-\s]', '', v)
        # Check if it's a valid ISBN-10 or ISBN-13
        if len(clean_isbn) == 10:
            # ISBN-10 validation
            if not re.match(r'^\d{9}[\dX]$', clean_isbn):
                raise ValueError('Invalid ISBN-10 format')
        elif len(clean_isbn) == 13:
            # ISBN-13 validation
            if not re.match(r'^97[89]\d{10}$', clean_isbn):
                raise ValueError('Invalid ISBN-13 format (must start with 978 or 979)')
            # Calculate checksum
            total = 0
            for i, digit in enumerate(clean_isbn[:12]):
                factor = 1 if i % 2 == 0 else 3
                total += int(digit) * factor
            check = (10 - (total % 10)) % 10
            if check != int(clean_isbn[12]):
                raise ValueError('Invalid ISBN-13 checksum')
        else:
            raise ValueError('ISBN must be 10 or 13 digits long')
        return v  # Return original with formatting

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    genre: Optional[str] = Field(None, max_length=100)
    published_year: Optional[int] = Field(None, ge=1000, le=2030)
    isbn: Optional[str] = Field(None, max_length=17)
    available: Optional[bool] = None

    @validator('isbn')
    def validate_isbn(cls, v):
        if v is None:
            return v
        # Same validation as in BookBase
        if v is None:
            return v
        clean_isbn = re.sub(r'[-\s]', '', v)
        if len(clean_isbn) == 10:
            if not re.match(r'^\d{9}[\dX]$', clean_isbn):
                raise ValueError('Invalid ISBN-10 format')
        elif len(clean_isbn) == 13:
            if not re.match(r'^97[89]\d{10}$', clean_isbn):
                raise ValueError('Invalid ISBN-13 format (must start with 978 or 979)')
            total = 0
            for i, digit in enumerate(clean_isbn[:12]):
                factor = 1 if i % 2 == 0 else 3
                total += int(digit) * factor
            check = (10 - (total % 10)) % 10
            if check != int(clean_isbn[12]):
                raise ValueError('Invalid ISBN-13 checksum')
        else:
            raise ValueError('ISBN must be 10 or 13 digits long')
        return v

class BookPatch(BaseModel):
    """For partial updates - all fields optional"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    genre: Optional[str] = Field(None, max_length=100)
    published_year: Optional[int] = Field(None, ge=1000, le=2030)
    isbn: Optional[str] = Field(None, max_length=17)
    available: Optional[bool] = None

    @validator('isbn')
    def validate_isbn(cls, v):
        if v is None:
            return v
        # Same validation as in BookBase
        if v is None:
            return v
        clean_isbn = re.sub(r'[-\s]', '', v)
        if len(clean_isbn) == 10:
            if not re.match(r'^\d{9}[\dX]$', clean_isbn):
                raise ValueError('Invalid ISBN-10 format')
        elif len(clean_isbn) == 13:
            if not re.match(r'^97[89]\d{10}$', clean_isbn):
                raise ValueError('Invalid ISBN-13 format (must start with 978 or 979)')
            total = 0
            for i, digit in enumerate(clean_isbn[:12]):
                factor = 1 if i % 2 == 0 else 3
                total += int(digit) * factor
            check = (10 - (total % 10)) % 10
            if check != int(clean_isbn[12]):
                raise ValueError('Invalid ISBN-13 checksum')
        else:
            raise ValueError('ISBN must be 10 or 13 digits long')
        return v

class BookResponse(BookBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BookListResponse(BaseModel):
    items: list[BookResponse]
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1, le=100)
    total: int = Field(..., ge=0)
    pages: int = Field(..., ge=0)
    has_next: bool = False
    has_prev: bool = False

    class Config:
        from_attributes = True