from __future__ import annotations

from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.books_repo import BooksRepository
from app.schemas.book import BookCreate, BookStatus
from app.models.book import Book


class BooksService:
    def __init__(self, repo: BooksRepository) -> None:
        self.repo = repo

    async def list_books(
        self,
        session: AsyncSession,
        status: Optional[BookStatus] = None,
        author: Optional[str] = None,
        limit: int = 10,
        cursor: Optional[str] = None,
    ) -> Sequence[Book]:
        return await self.repo.list_books(
            session=session,
            status=status,
            author=author,
            limit=limit,
            cursor=cursor,
        )

    async def get_book(self, session: AsyncSession, book_id: str) -> Optional[Book]:
        return await self.repo.get_by_id(session, book_id)

    async def create_book(self, session: AsyncSession, payload: BookCreate) -> Book:
        return await self.repo.add(session, payload)

    async def delete_book(self, session: AsyncSession, book_id: str) -> bool:
        return await self.repo.delete(session, book_id)