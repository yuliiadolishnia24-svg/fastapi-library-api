import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_lifecycle_and_pagination():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Створення книги
        post_resp = await ac.post("/books", json={
            "title": "Postgres Book", "author": "John Doe", "release_year": 2026, "status": "available"
        })
        assert post_resp.status_code == 201
        book_id = post_resp.json()["id"]

        # 2. Отримання по ID
        get_id_resp = await ac.get(f"/books/{book_id}")
        assert get_id_resp.status_code == 200

        # 3. Перевірка Limit-Offset пагінації та фільтрації
        get_all_resp = await ac.get("/books", params={"skip": 0, "limit": 5, "status": "available"})
        assert get_all_resp.status_code == 200
        assert len(get_all_resp.json()) >= 1

        # 4. Ідемпотентне видалення
        del_resp1 = await ac.delete(f"/books/{book_id}")
        assert del_resp1.status_code == 204
        del_resp2 = await ac.delete(f"/books/{book_id}") # другий раз теж має повернути 204
        assert del_resp2.status_code == 204