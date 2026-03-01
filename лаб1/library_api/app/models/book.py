import uuid
from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class Book(Base):
    __tablename__ = "books"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # available | issued
    year: Mapped[int] = mapped_column(Integer, nullable=False)