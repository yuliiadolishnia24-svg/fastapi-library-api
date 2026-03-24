# tests/test_books.py
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_create_and_get_book():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Створення книги
        payload = {"title": "Kobzar", "author": "Shevchenko", "release_year": 1840}
        response = await ac.post("/books/", json=payload)
        assert response.status_code == 201
        book_id = response.json()["id"]

        # 2. Отримання по ID
        response = await ac.get(f"/books/{book_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Kobzar"

@pytest.mark.asyncio
async def test_delete_idempotency():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/books/", json={"title": "Test", "author": "A", "release_year": 2024})
        b_id = res.json()["id"]
        
        # Видаляємо двічі
        res1 = await ac.delete(f"/books/{b_id}")
        assert res1.status_code == 204
        res2 = await ac.delete(f"/books/{b_id}")
        assert res2.status_code == 204