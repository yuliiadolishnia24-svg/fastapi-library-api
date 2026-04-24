from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from models.database import get_db
from models.book_model import BookDB
from schemas.book import Book, BookCreate

router = APIRouter()

@router.get("", response_model=List[Book])
def get_all_books(
    limit: int = Query(10, ge=1, le=100, description="Кількість записів"),
    last_id: Optional[UUID] = Query(None, description="ID останньої книги з попередньої сторінки"),
    db: Session = Depends(get_db)
):
    query = db.query(BookDB)
    
    if last_id:
        # Курсорна пагінація: вибираємо записи, що йдуть після вказаного ID
        # Примітка: для UUID сортування зазвичай йде за часом створення або алфавітом
        query = query.filter(BookDB.id > last_id)
    
    # Сортування за ID обов'язкове для стабільності курсора
    return query.order_by(BookDB.id).limit(limit).all()

@router.post("", response_model=Book, status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = BookDB(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book