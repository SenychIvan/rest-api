from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status, Query

from app.repository.books_repo import BooksRepository
from app.schemas.book import BookCreate, BookOut, BookStatus
from app.services.books import BooksService

router = APIRouter(prefix="/books", tags=["books"])

repo = BooksRepository()
service = BooksService(repo)


@router.get("", response_model=List[BookOut], status_code=status.HTTP_200_OK)
async def get_books(
    status_: Optional[BookStatus] = Query(default=None, alias="status"),
    author: Optional[str] = Query(default=None),
    sort_by: Optional[str] = Query(default=None, pattern="^(title|year)?$"),
    order: str = Query(default="asc", pattern="^(asc|desc)$"),
):
    books = await service.list_books(status=status_, author=author, sort_by=sort_by, order=order)
    return books


@router.get("/{book_id}", response_model=BookOut, status_code=status.HTTP_200_OK)
async def get_book_by_id(book_id: UUID):
    book = await service.get_book(book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@router.post("", response_model=BookOut, status_code=status.HTTP_201_CREATED)
async def create_book(payload: BookCreate):
    book = await service.create_book(payload)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: UUID):
    await service.delete_book(book_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)