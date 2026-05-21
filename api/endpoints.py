from fastapi import APIRouter, Depends, Query, HTTPException, Response
from pydantic_mongo import PydanticObjectId
from typing import List, Optional
from models.database import get_books_collection
from schemas.book import Book, BookCreate
# Імпортуємо функцію перевірки токена з сервісу автентифікації
from services.auth import get_current_user_id

router = APIRouter()

# 1. Створення книги (POST) — ЗАХИЩЕНИЙ ЕНДПОІНТ
@router.post("", response_model=Book, status_code=201)
async def create_book(
    book: BookCreate, 
    collection = Depends(get_books_collection),
    current_user_id: str = Depends(get_current_user_id)  # Вимагає валідний Access Token
):
    book_dict = book.model_dump()
    result = await collection.insert_one(book_dict)
    
    # Повертаємо створений об'єкт разом з новим _id від MongoDB
    inserted_book = await collection.find_one({"_id": result.inserted_id})
    return inserted_book


# 2. Отримання всіх книг (GET) з Limit-Offset пагінацією та фільтрами — ВІДКРИТИЙ
@router.get("", response_model=List[Book])
async def get_all_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    collection = Depends(get_books_collection)
):
    search_filter = {}
    if status:
        search_filter["status"] = status
    if author:
        # Регістронезалежний пошук (аналог ilike)
        search_filter["author"] = {"$regex": author, "$options": "i"}
        
    cursor = collection.find(search_filter).skip(skip).limit(limit)
    books = await cursor.to_list(length=limit)
    return books


# 3. Отримання однієї книги за ID (GET) — ВІДКРИТИЙ
@router.get("/{book_id}", response_model=Book)
async def get_book_by_id(book_id: str, collection = Depends(get_books_collection)):
    try:
        obj_id = PydanticObjectId(book_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")
        
    book = await collection.find_one({"_id": obj_id})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


# 4. Видалення книги за ID (DELETE) — ЗАХИЩЕНИЙ ЕНДПОІНТ
@router.delete("/{book_id}", status_code=204)
async def delete_book(
    book_id: str, 
    collection = Depends(get_books_collection),
    current_user_id: str = Depends(get_current_user_id)  # Вимагає валідний Access Token
):
    try:
        obj_id = PydanticObjectId(book_id)
    except Exception:
        # Для ідемпотентності, якщо формат ID битий, повертаємо 204
        return Response(status_code=204)
        
    response = await collection.delete_one({"_id": obj_id})
    return Response(status_code=204)