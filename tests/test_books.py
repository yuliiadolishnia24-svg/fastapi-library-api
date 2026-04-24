import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_create_book():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as ac:
        response = await ac.post("/books", json={
            "title": "Lab 3 Book",
            "author": "Author Name",
            "release_year": 2026,
            "description": "Test for Lab 3",
            "status": "available"
        })
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_get_books_cursor_pagination():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as ac:
        # Отримуємо першу книгу, щоб взяти її ID як курсор
        first_resp = await ac.get("/books", params={"limit": 1})
        books = first_resp.json()
        
        if len(books) > 0:
            cursor_id = books[0]["id"]
            # Запит з використанням last_id
            response = await ac.get("/books", params={"limit": 5, "last_id": cursor_id})
            assert response.status_code == 200