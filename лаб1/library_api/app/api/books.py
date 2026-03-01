from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.book import BookCreate, BookOut, BookStatus
from app.services.books import BooksService
from app.repository.books_repo import BooksRepository

router = APIRouter(prefix="/books", tags=["books"])
service = BooksService(BooksRepository())


@router.get("", response_model=List[BookOut], status_code=200)
async def get_books(
    session: AsyncSession = Depends(get_session),
    status_: Optional[BookStatus] = Query(default=None, alias="status"),
    author: Optional[str] = Query(default=None),
    sort_by: Optional[str] = Query(default=None, pattern="^(title|year)?$"),
    order: str = Query(default="asc", pattern="^(asc|desc)$"),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    books = await service.list_books(
        session=session,
        status=status_,
        author=author,
        sort_by=sort_by,
        order=order,
        limit=limit,
        offset=offset,
    )
    return books


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
    # ідемпотентно
    await service.delete_book(session, book_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)