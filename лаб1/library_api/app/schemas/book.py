from __future__ import annotations

from enum import Enum
from typing import List
from pydantic import BaseModel, Field


class BookStatus(str, Enum):
    available = "available"
    issued = "issued"


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)
    status: BookStatus = BookStatus.available
    year: int = Field(ge=0, le=2100)


class BookOut(BookCreate):
    id: str


class BookListResponse(BaseModel):
    items: List[BookOut]
    total: int
    limit: int
    offset: int