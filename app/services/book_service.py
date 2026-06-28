from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import book_repository as crud_book
from app.schemas.book import BookCreate, BookUpdate, BookResponse, BookListResponse
from app.exceptions.custom_exceptions import NotFoundException

async def get_book(db: AsyncSession, book_id: int) -> BookResponse:
    """Get a single book by ID"""
    book = await crud_book.get_book_by_id(db, book_id)
    if not book:
        raise NotFoundException(f"Book with id {book_id} not found")
    return BookResponse.from_orm(book)

async def get_books(
    db: AsyncSession,
    page: int = 1,
    limit: int = 10,
    title: str = None,
    author: str = None,
    isbn: str = None,
    is_available: bool = None
) -> BookListResponse:
    """Get list of books with pagination and filtering"""
    # Validate pagination parameters
    if page < 1:
        page = 1
    if limit < 1:
        limit = 10
    if limit > 100:  # Max limit as per requirements
        limit = 100

    # Calculate offset
    skip = (page - 1) * limit

    # Get books and total count
    books, total = await crud_book.get_books(
        db,
        skip=skip,
        limit=limit,
        title=title,
        author=author,
        isbn=isbn,
        is_available=is_available
    )

    # Calculate pagination metadata
    pages = (total + limit - 1) // limit if total > 0 else 0
    has_next = page < pages
    has_prev = page > 1

    return BookListResponse(
        items=[BookResponse.from_orm(book) for book in books],
        page=page,
        limit=limit,
        total=total,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev
    )

async def create_book(db: AsyncSession, book_in: BookCreate) -> BookResponse:
    """Create a new book"""
    book = await crud_book.create_book(db, book_in=book_in)
    return BookResponse.from_orm(book)

async def update_book(db: AsyncSession, book_id: int, book_in: BookUpdate) -> BookResponse:
    """Update a book completely"""
    book = await crud_book.update_book(db, book_id=book_id, book_in=book_in)
    if not book:
        raise NotFoundException(f"Book with id {book_id} not found")
    return BookResponse.from_orm(book)

async def patch_book(db: AsyncSession, book_id: int, book_in) -> BookResponse:
    """Partially update a book"""
    book = await crud_book.patch_book(db, book_id=book_id, book_in=book_in)
    if not book:
        raise NotFoundException(f"Book with id {book_id} not found")
    return BookResponse.from_orm(book)

async def delete_book(db: AsyncSession, book_id: int) -> None:
    """Delete a book"""
    book = await crud_book.delete_book(db, book_id=book_id)
    if not book:
        raise NotFoundException(f"Book with id {book_id} not found")