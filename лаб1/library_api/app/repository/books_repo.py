from __future__ import annotations

from typing import Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from app.schemas.book import BookCreate, BookStatus


class BooksRepository:
    @staticmethod
    def _serialize(book: dict) -> dict:
        return {
            "id": str(book["_id"]),
            "title": book["title"],
            "author": book["author"],
            "description": book["description"],
            "status": book["status"],
            "year": book["year"],
        }

    async def list_books(
        self,
        collection: AsyncIOMotorCollection,
        status: Optional[BookStatus],
        author: Optional[str],
        sort_by: Optional[str],
        order: str,
        limit: int,
        offset: int,
    ) -> tuple[list[dict], int]:
        query = {}

        if status is not None:
            query["status"] = status.value

        if author is not None:
            query["author"] = author

        sort_direction = 1 if order == "asc" else -1
        sort_field = sort_by if sort_by in {"title", "year"} else "_id"

        total = await collection.count_documents(query)

        cursor = (
            collection.find(query)
            .sort(sort_field, sort_direction)
            .skip(offset)
            .limit(limit)
        )

        books = [self._serialize(book) async for book in cursor]
        return books, total

    async def get_by_id(
        self,
        collection: AsyncIOMotorCollection,
        book_id: str,
    ) -> Optional[dict]:
        if not ObjectId.is_valid(book_id):
            return None

        book = await collection.find_one({"_id": ObjectId(book_id)})
        if book is None:
            return None

        return self._serialize(book)

    async def add(
        self,
        collection: AsyncIOMotorCollection,
        payload: BookCreate,
    ) -> dict:
        book_data = payload.model_dump()
        result = await collection.insert_one(book_data)
        created = await collection.find_one({"_id": result.inserted_id})
        return self._serialize(created)

    async def delete(
        self,
        collection: AsyncIOMotorCollection,
        book_id: str,
    ) -> bool:
        if not ObjectId.is_valid(book_id):
            return False

        result = await collection.delete_one({"_id": ObjectId(book_id)})
        return result.deleted_count > 0