import pytest


@pytest.mark.anyio
async def test_create_and_get(client):
    payload = {
        "title": "Dune",
        "author": "Frank Herbert",
        "description": "Sci-fi",
        "status": "available",
        "year": 1965
    }
    r = await client.post("/books", json=payload)
    assert r.status_code == 201
    book = r.json()
    assert "id" in book

    r2 = await client.get(f"/books/{book['id']}")
    assert r2.status_code == 200
    assert r2.json()["title"] == "Dune"


@pytest.mark.anyio
async def test_limit_offset_pagination(client):
    # додаємо 5 книг
    for i in range(5):
        await client.post("/books", json={
            "title": f"Book {i}",
            "author": "Ivan",
            "description": "",
            "status": "available",
            "year": 2000 + i
        })

    r1 = await client.get("/books", params={"limit": 2, "offset": 0})
    assert r1.status_code == 200
    assert len(r1.json()) == 2

    r2 = await client.get("/books", params={"limit": 2, "offset": 4})
    assert r2.status_code == 200
    assert len(r2.json()) == 1


@pytest.mark.anyio
async def test_delete_idempotent(client):
    r = await client.post("/books", json={
        "title": "To delete",
        "author": "Me",
        "description": "",
        "status": "available",
        "year": 2020
    })
    book_id = r.json()["id"]

    d1 = await client.delete(f"/books/{book_id}")
    assert d1.status_code == 204

    d2 = await client.delete(f"/books/{book_id}")
    assert d2.status_code == 204