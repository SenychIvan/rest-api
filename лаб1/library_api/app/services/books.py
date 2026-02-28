from __future__ import annotations

from typing import Dict, List, Optional
from uuid import UUID, uuid4

from app.repository.books_repo import BooksRepository
from app.schemas.book import BookCreate, BookStatus


class BooksService:
    def __init__(self, repo: BooksRepository) -> None:
        self.repo = repo

    async def list_books(
        self,
        status: Optional[BookStatus] = None,
        author: Optional[str] = None,
        sort_by: Optional[str] = None,   # "title" | "year"
        order: str = "asc",              # "asc" | "desc"
    ) -> List[Dict]:
        books = list(await self.repo.list_books())

        if status is not None:
            books = [b for b in books if b["status"] == status.value]

        if author is not None:
            # простий case-insensitive exact match; можна змінити на contains
            a = author.strip().lower()
            books = [b for b in books if b["author"].strip().lower() == a]

        if sort_by in {"title", "year"}:
            reverse = (order == "desc")
            if sort_by == "title":
                books.sort(key=lambda x: (x["title"] or "").lower(), reverse=reverse)
            else:
                books.sort(key=lambda x: x["year"], reverse=reverse)

        return books

    async def get_book(self, book_id: UUID) -> Optional[Dict]:
        return await self.repo.get_by_id(book_id)

    async def create_book(self, payload: BookCreate) -> Dict:
        book = payload.model_dump()
        book["id"] = str(uuid4())  # UUID генеруємо автоматично
        return await self.repo.add(book)

    async def delete_book(self, book_id: UUID) -> bool:
        return await self.repo.delete(book_id)