from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.book import BookCreate, BookOut, BookStatus, BookListResponse
from app.services.books import BooksService
from app.repository.books_repo import BooksRepository

router = APIRouter(prefix="/books", tags=["books"])
service = BooksService(BooksRepository())


@router.get("", response_model=BookListResponse, status_code=200)
async def get_books(
    session: AsyncSession = Depends(get_session),
    status_: Optional[BookStatus] = Query(default=None, alias="status"),
    author: Optional[str] = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
    cursor: Optional[str] = Query(default=None),
):
    books = await service.list_books(
        session=session,
        status=status_,
        author=author,
        limit=limit,
        cursor=cursor,
    )

    next_cursor = books[-1].id if len(books) == limit else None

    return BookListResponse(
        items=books,
        next_cursor=next_cursor,
    )


@router.get("/{book_id}", response_model=BookOut, status_code=200)
async def get_book_by_id(
    book_id: str,
    session: AsyncSession = Depends(get_session),
):
    book = await service.get_book(session, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("", response_model=BookOut, status_code=201)
async def create_book(
    payload: BookCreate,
    session: AsyncSession = Depends(get_session),
):
    return await service.create_book(session, payload)


@router.delete("/{book_id}", status_code=204)
async def delete_book(
    book_id: str,
    session: AsyncSession = Depends(get_session),
):
    await service.delete_book(session, book_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)