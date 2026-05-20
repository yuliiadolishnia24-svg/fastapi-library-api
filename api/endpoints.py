from fastapi import APIRouter, Depends, Query, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

# Імпорт залежностей, моделей та схем
from models.database import get_db
from models.book_model import BookDB
from schemas.book import Book, BookCreate

router = APIRouter()

# 1. Додавання книги (POST)
@router.post("", response_model=Book, status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = BookDB(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# 2. Отримання всіх книг (GET) з пагінацією, фільтрацією та сортуванням
@router.get("", response_model=List[Book])
def get_all_books(
    skip: int = Query(0, ge=0, description="Offset (скільки книг пропустити)"),
    limit: int = Query(10, ge=1, le=100, description="Limit (скільки книг повернути)"),
    status: Optional[str] = Query(None, description="Фільтр за статусом (available/issued)"),
    author: Optional[str] = Query(None, description="Фільтр за автором"),
    sort_by: Optional[str] = Query(None, description="Сортування: title або release_year"),
    db: Session = Depends(get_db)
):
    query = db.query(BookDB)
    
    # Фільтрація (Лабораторна №1)
    if status:
        query = query.filter(BookDB.status == status)
    if author:
        query = query.filter(BookDB.author.ilike(f"%{author}%"))
        
    # Сортування (Лабораторна №1)
    if sort_by == "title":
        query = query.order_by(BookDB.title)
    elif sort_by == "release_year":
        query = query.order_by(BookDB.release_year)
    else:
        query = query.order_by(BookDB.id)  # сортування за замовчуванням
        
    # Limit-Offset пагінація (Лабораторна №2)
    return query.offset(skip).limit(limit).all()

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