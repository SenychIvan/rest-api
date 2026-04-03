from __future__ import annotations

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorCollection

from app.repository.books_repo import BooksRepository
from app.schemas.book import BookCreate, BookStatus


class BooksService:
    def __init__(self, repo: BooksRepository) -> None:
        self.repo = repo

    async def list_books(
        self,
        collection: AsyncIOMotorCollection,
        status: Optional[BookStatus] = None,
        author: Optional[str] = None,
        sort_by: Optional[str] = None,
        order: str = "asc",
        limit: int = 10,
        offset: int = 0,
    ):
        return await self.repo.list_books(
            collection=collection,
            status=status,
            author=author,
            sort_by=sort_by,
            order=order,
            limit=limit,
            offset=offset,
        )

    async def get_book(self, collection: AsyncIOMotorCollection, book_id: str):
        return await self.repo.get_by_id(collection, book_id)

    async def create_book(self, collection: AsyncIOMotorCollection, payload: BookCreate):
        return await self.repo.add(collection, payload)

    async def delete_book(self, collection: AsyncIOMotorCollection, book_id: str):
        return await self.repo.delete(collection, book_id)