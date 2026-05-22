from fastapi import APIRouter, Depends, Query, HTTPException, Response, Request
from pydantic_mongo import PydanticObjectId
from typing import List, Optional
from models.database import get_books_collection
from schemas.book import Book, BookCreate
from services.auth import get_current_user_id
# Імпортуємо наш лімітер
from services.rate_limiter import check_rate_limit

router = APIRouter()

# 1. Отримання всіх книг (GET) — ПУБЛІЧНИЙ (Анонімний ліміт: 2 зап/хв)
@router.get("", response_model=List[Book])
async def get_all_books(
    request: Request, # Потрібно для отримання host клієнта
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    collection = Depends(get_books_collection)
):
    # Перевіряємо токен, але не падаємо, якщо його немає (анонімний режим)
    from services.auth import api_key_scheme, SECRET_KEY, ALGORITHM
    import jwt
    
    user_id = None
    token = await api_key_scheme(request)
    if token:
        try:
            if token.startswith("Bearer ") or token.startswith("bearer "):
                token = token.split(" ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
        except:
            pass # Якщо токен битий, користувач розглядається як анонімний
            
    # Запускаємо Rate Limiter
    await check_rate_limit(request, user_id=user_id)
    
    cursor = collection.find({}).skip(skip).limit(limit)
    return await cursor.to_list(length=limit)


# 2. Створення книги (POST) — АВТОРИЗОВАНИЙ (Ліміт: 10 зап/хв)
@router.post("", response_model=Book, status_code=201)
async def create_book(
    request: Request,
    book: BookCreate, 
    collection = Depends(get_books_collection),
    current_user_id: str = Depends(get_current_user_id)
):
    # Запускаємо Rate Limiter з передачею конкретного ID користувача
    await check_rate_limit(request, user_id=current_user_id)
    
    book_dict = book.model_dump()
    result = await collection.insert_one(book_dict)
    inserted_book = await collection.find_one({"_id": result.inserted_id})
    return inserted_book