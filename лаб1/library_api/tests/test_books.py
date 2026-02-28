import pytest
from httpx import AsyncClient, ASGITransport
from uuid import UUID

from app.main import app
from app.models.storage import BOOKS


@pytest.mark.asyncio
async def test_get_books_empty():
    BOOKS.clear()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/books")

    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_create_and_get_by_id():
    BOOKS.clear()
    transport = ASGITransport(app=app)

    payload = {
        "title": "Dune",
        "author": "Frank Herbert",
        "description": "Sci-fi",
        "status": "available",
        "year": 1965
    }

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/books", json=payload)
        assert r.status_code == 201

        data = r.json()
        assert "id" in data
        UUID(data["id"])  

        book_id = data["id"]

        r2 = await ac.get(f"/books/{book_id}")
        assert r2.status_code == 200
        assert r2.json()["title"] == "Dune"


@pytest.mark.asyncio
async def test_get_by_id_not_found():
    BOOKS.clear()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/books/00000000-0000-0000-0000-000000000000")

    assert r.status_code == 404


@pytest.mark.asyncio
async def test_filter_and_sort():
    BOOKS.clear()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post("/books", json={
            "title": "C Book",
            "author": "Ivan",
            "description": "",
            "status": "issued",
            "year": 2000
        })

        await ac.post("/books", json={
            "title": "A Book",
            "author": "Ivan",
            "description": "",
            "status": "available",
            "year": 1990
        })

        await ac.post("/books", json={
            "title": "B Book",
            "author": "Other",
            "description": "",
            "status": "available",
            "year": 2010
        })

        r = await ac.get(
            "/books",
            params={
                "author": "Ivan",
                "status": "available",
                "sort_by": "title",
                "order": "asc"
            }
        )

        assert r.status_code == 200
        items = r.json()
        assert len(items) == 1
        assert items[0]["title"] == "A Book"

        r2 = await ac.get("/books", params={"sort_by": "year", "order": "desc"})
        years = [x["year"] for x in r2.json()]
        assert years == sorted(years, reverse=True)


@pytest.mark.asyncio
async def test_delete_idempotent():
    BOOKS.clear()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/books", json={
            "title": "To delete",
            "author": "Me",
            "description": "",
            "status": "available",
            "year": 2020
        })

        book_id = r.json()["id"]

        d1 = await ac.delete(f"/books/{book_id}")
        assert d1.status_code == 204

        d2 = await ac.delete(f"/books/{book_id}")
        assert d2.status_code == 204