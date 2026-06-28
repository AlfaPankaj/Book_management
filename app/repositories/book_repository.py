from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate
from app.exceptions.custom_exceptions import ConflictException

async def get_book_by_id(db: AsyncSession, book_id: int):
    result = await db.execute(select(Book).where(Book.id == book_id))
    return result.scalar_one_or_none()

async def get_books(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    title: str = None,
    author: str = None,
    isbn: str = None,
    is_available: bool = None
):
    query = select(Book)

    # Build filters
    filters = []
    if title:
        filters.append(Book.title.ilike(f"%{title}%"))
    if author:
        filters.append(Book.author.ilike(f"%{author}%"))
    if isbn:
        filters.append(Book.isbn == isbn)
    if is_available is not None:
        filters.append(Book.available == is_available)

    if filters:
        query = query.where(and_(*filters))

    # Get total count
    count_query = select(func.count()).select_from(Book)
    if filters:
        count_query = count_query.where(and_(*filters))

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(Book.created_at.desc())
    result = await db.execute(query)
    books = result.scalars().all()

    return books, total

async def create_book(db: AsyncSession, book_in: BookCreate):
    # Check if ISBN already exists
    if book_in.isbn:
        result = await db.execute(select(Book).where(Book.isbn == book_in.isbn))
        existing_book = result.scalar_one_or_none()
        if existing_book:
            raise ConflictException(f"Book with ISBN {book_in.isbn} already exists")

    book = Book(**book_in.dict())
    db.add(book)
    try:
        await db.commit()
        await db.refresh(book)
    except IntegrityError as e:
        await db.rollback()
        if "isbn" in str(e).lower():
            raise ConflictException(f"Book with ISBN {book_in.isbn} already exists")
        raise
    return book

async def update_book(db: AsyncSession, book_id: int, book_in: BookUpdate):
    book = await get_book_by_id(db, book_id)
    if not book:
        return None

    # Check ISBN uniqueness if being updated
    update_data = book_in.dict(exclude_unset=True)
    if 'isbn' in update_data and update_data['isbn']:
        result = await db.execute(
            select(Book).where(and_(Book.isbn == update_data['isbn'], Book.id != book_id))
        )
        existing_book = result.scalar_one_or_none()
        if existing_book:
            raise ConflictException(f"Book with ISBN {update_data['isbn']} already exists")

    # Update fields
    for field, value in update_data.items():
        setattr(book, field, value)

    db.add(book)
    try:
        await db.commit()
        await db.refresh(book)
    except IntegrityError as e:
        await db.rollback()
        if "isbn" in str(e).lower():
            raise ConflictException(f"Book with ISBN {update_data.get('isbn', book.isbn)} already exists")
        raise
    return book

async def patch_book(db: AsyncSession, book_id: int, book_in):
    book = await get_book_by_id(db, book_id)
    if not book:
        return None

    # Get only the fields that were provided (not None)
    update_data = book_in.dict(exclude_unset=True)

    # Check ISBN uniqueness if being updated
    if 'isbn' in update_data and update_data['isbn']:
        result = await db.execute(
            select(Book).where(and_(Book.isbn == update_data['isbn'], Book.id != book_id))
        )
        existing_book = result.scalar_one_or_none()
        if existing_book:
            raise ConflictException(f"Book with ISBN {update_data['isbn']} already exists")

    # Update fields
    for field, value in update_data.items():
        setattr(book, field, value)

    db.add(book)
    try:
        await db.commit()
        await db.refresh(book)
    except IntegrityError as e:
        await db.rollback()
        if "isbn" in str(e).lower():
            raise ConflictException(f"Book with ISBN {update_data.get('isbn', book.isbn)} already exists")
        raise
    return book

async def delete_book(db: AsyncSession, book_id: int):
    book = await get_book_by_id(db, book_id)
    if book:
        await db.delete(book)
        await db.commit()
    return book