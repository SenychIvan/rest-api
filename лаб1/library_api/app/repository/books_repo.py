from __future__ import annotations

from typing import Optional, Sequence
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import Book
from app.schemas.book import BookCreate, BookStatus


class BooksRepository:
    async def list_books(
        self,
        session: AsyncSession,
        status: Optional[BookStatus],
        author: Optional[str],
        sort_by: Optional[str],
        order: str,
        limit: int,
        cursor: Optional[str],
    ) -> Sequence[Book]:
        stmt = select(Book)

        if status is not None:
            stmt = stmt.where(Book.status == status.value)

        if author is not None:
            stmt = stmt.where(Book.author.ilike(author))

        # Для cursor pagination робимо стабільне сортування по id
        # sort_by/order лишаємо в API як сумісність, але для курсора
        # основна логіка йде по id.
        if cursor:
            stmt = stmt.where(Book.id > cursor)

        stmt = stmt.order_by(Book.id.asc()).limit(limit)
        res = await session.execute(stmt)
        return res.scalars().all()

    async def get_by_id(self, session: AsyncSession, book_id: str) -> Optional[Book]:
        res = await session.execute(select(Book).where(Book.id == book_id))
        return res.scalar_one_or_none()

    async def add(self, session: AsyncSession, payload: BookCreate) -> Book:
        book = Book(**payload.model_dump())
        session.add(book)
        await session.commit()
        await session.refresh(book)
        return book

    async def delete(self, session: AsyncSession, book_id: str) -> bool:
        res = await session.execute(delete(Book).where(Book.id == book_id))
        await session.commit()
        return (res.rowcount or 0) > 0