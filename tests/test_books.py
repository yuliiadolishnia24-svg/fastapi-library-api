import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from services.auth import create_tokens
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_lifecycle_and_pagination(mocker):
    # Головний об'єкт колекції — AsyncMock
    mock_collection = AsyncMock()
    
    # Імітуємо успішний insert_one
    mock_result = MagicMock()
    mock_result.inserted_id = "6a0f53aaaa2e9733d3d6d08d"
    mock_collection.insert_one.return_value = mock_result
    
    # Імітуємо повернення однієї книги для find_one
    fake_book = {
        "_id": "6a0f53aaaa2e9733d3d6d08d",
        "title": "Postgres Book", 
        "author": "John Doe", 
        "release_year": 2026, 
        "status": "available"
    }
    mock_collection.find_one.return_value = fake_book
    
    # --- НАШ ФІКС ТУТ ---
    # Створюємо СИНХРОННИЙ MagicMock для курсора
    mock_cursor = MagicMock()
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    # А ось сам метод отримання даних зі списку — асинхронний
    mock_cursor.to_list = AsyncMock(return_value=[fake_book])
    
    # Примусово кажемо, що find — це звичайна синхронна функція, яка повертає курсор
    mock_collection.find = MagicMock(return_value=mock_cursor)
    # ---------------------

    # Підміняємо реальне підключення FastAPI до бази на наш мок
    from models.database import get_books_collection
    app.dependency_overrides[get_books_collection] = lambda: mock_collection

    # Повністю вимикаємо перевірку лімітера під час цього тесту
    mocker.patch("api.endpoints.check_rate_limit", new_callable=AsyncMock)

    tokens = create_tokens("test_user_id_123")
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        
        # 1. Створення книги
        post_resp = await ac.post("/books", json={
            "title": "Postgres Book", 
            "author": "John Doe", 
            "release_year": 2026, 
            "status": "available"
        }, headers=headers)
        
        assert post_resp.status_code == 201
        created_book = post_resp.json()
        assert created_book["title"] == "Postgres Book"

        # 2. Отримання списку книг з пагінацією
        get_resp = await ac.get("/books?skip=0&limit=10", headers=headers)
        assert get_resp.status_code == 200
        books_list = get_resp.json()
        assert len(books_list) > 0

    # Очищуємо підміну після завершення тесту
    app.dependency_overrides.clear()