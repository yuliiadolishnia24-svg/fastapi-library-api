from fastapi import APIRouter, Depends, Query, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

# Імпорт залежностей, моделей та схем
from models.database import get_db
from models.book_model import BookDB
from schemas.book import Book, BookCreate, BookPaginationResponse

router = APIRouter()

# 1. Додавання книги (POST)
@router.post("", response_model=Book, status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = BookDB(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# 2. Отримання всіх книг (GET) з CURSOR пагінацією та фільтрацією
@router.get("", response_model=BookPaginationResponse)
def get_all_books(
    limit: int = Query(10, ge=1, le=100, description="Скільки книг повернути"),
    cursor: Optional[UUID] = Query(None, description="ID останньої книги з попередньої сторінки"),
    status: Optional[str] = Query(None, description="Фільтр за статусом (available/issued)"),
    author: Optional[str] = Query(None, description="Фільтр за автором"),
    db: Session = Depends(get_db)
):
    # Починаємо базовий запит і обов'язково сортуємо за ID для стабільності курсору
    query = db.query(BookDB).order_by(BookDB.id)
    
    # Фільтрація (з ЛР №1)
    if status:
        query = query.filter(BookDB.status == status)
    if author:
        query = query.filter(BookDB.author.ilike(f"%{author}%"))
        
    
    # Якщо курсор передано, беремо лише записи, які йдуть ПІСЛЯ цього курсору
    if cursor:
        query = query.filter(BookDB.id > cursor)
        
    # Запитуємо на 1 елемент БІЛЬШЕ, ніж просив клієнт (limit + 1),
    # щоб дізнатися, чи є взагалі наступна сторінка
    books = query.limit(limit + 1).all()
    
    has_more = len(books) > limit
    next_cursor = None
    
    if has_more:
        # Відрізаємо той самий "+1" зайвий елемент
        books = books[:limit]
        # Записуємо ID останньої книги в цій сторінці як маркер (курсор) для наступної
        next_cursor = str(books[-1].id)
        
    return BookPaginationResponse(items=books, next_cursor=next_cursor)

# 3. Отримання книги за ID (GET)
@router.get("/{book_id}", response_model=Book)
def get_book_by_id(book_id: UUID, db: Session = Depends(get_db)):
    book = db.query(BookDB).filter(BookDB.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# 4. Видалення книги за ID (DELETE) — Ідемпотентне
@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: UUID, db: Session = Depends(get_db)):
    book = db.query(BookDB).filter(BookDB.id == book_id).first()
    if book:
        db.delete(book)
        db.commit()
    # Ідемпотентність: навіть якщо книга вже видалена, повертаємо 204 No Content без помилки
    return Response(status_code=204)