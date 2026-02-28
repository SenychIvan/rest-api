from __future__ import annotations

from typing import Dict, List, Optional
from uuid import UUID

from app.models.storage import BOOKS


class BooksRepository:
    async def list_books(self) -> List[Dict]:
        return BOOKS

    async def get_by_id(self, book_id: UUID) -> Optional[Dict]:
        for b in BOOKS:
            if b["id"] == str(book_id):
                return b
        return None

    async def add(self, book: Dict) -> Dict:
        BOOKS.append(book)
        return book

    async def delete(self, book_id: UUID) -> bool:
        """
        Повертає True якщо видалили, False якщо не знайшли.
        DELETE робитимемо ідемпотентним на рівні API (204 в обох випадках).
        """
        idx_to_delete = None
        for i, b in enumerate(BOOKS):
            if b["id"] == str(book_id):
                idx_to_delete = i
                break
        if idx_to_delete is None:
            return False
        BOOKS.pop(idx_to_delete)
        return True