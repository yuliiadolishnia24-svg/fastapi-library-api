import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_create_book():
    transport = ASGITransport(app=app)
    # follow_redirects=True дозволить клієнту самому проходити через 307 статус
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as ac:
        response = await ac.post("/books/", json={
            "title": "Test Book",
            "author": "Test Author",
            "release_year": 2024,
            "description": "Test Description",
            "status": "available"
        })
    
    assert response.status_code == 201
    assert response.json()["title"] == "Test Book"

@pytest.mark.asyncio
async def test_get_books_pagination():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as ac:
        response = await ac.get("/books/", params={"skip": 0, "limit": 5})
        
    assert response.status_code == 200
    assert isinstance(response.json(), list)