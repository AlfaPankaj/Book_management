from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.schemas.book import BookCreate, BookUpdate, BookPatch, BookResponse, BookListResponse
from app.services.book_service import (
    get_book,
    get_books,
    create_book,
    update_book,
    patch_book,
    delete_book
)
from app.core.security import get_current_active_user
from app.schemas.user import User

router = APIRouter()

@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book_endpoint(
    book_in: BookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new book.
    Requires authentication.
    """
    return await create_book(db=db, book_in=book_in)

@router.get("/", response_model=BookListResponse)
async def read_books(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    title: Optional[str] = Query(None, description="Filter by title (partial match)"),
    author: Optional[str] = Query(None, description="Filter by author (partial match)"),
    isbn: Optional[str] = Query(None, description="Filter by exact ISBN"),
    available: Optional[bool] = Query(None, description="Filter by availability"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List books with pagination and filtering.
    Requires authentication.
    Supports filtering by title, author, ISBN, and availability.
    """
    return await get_books(
        db=db,
        page=page,
        limit=limit,
        title=title,
        author=author,
        isbn=isbn,
        is_available=available
    )

@router.get("/{book_id}", response_model=BookResponse)
async def read_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific book by ID.
    Requires authentication.
    """
    return await get_book(db=db, book_id=book_id)

@router.put("/{book_id}", response_model=BookResponse)
async def update_book_endpoint(
    book_id: int,
    book_in: BookUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a book completely (PUT).
    Requires authentication.
    """
    return await update_book(db=db, book_id=book_id, book_in=book_in)

@router.patch("/{book_id}", response_model=BookResponse)
async def patch_book_endpoint(
    book_id: int,
    book_in: BookPatch,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a book partially (PATCH).
    Requires authentication.
    Only updates fields that are provided.
    """
    return await patch_book(db=db, book_id=book_id, book_in=book_in)

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book_endpoint(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a book.
    Requires authentication.
    """
    await delete_book(db=db, book_id=book_id)
    return None