from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models.database import get_db
from models.book_model import BookDB
from schemas.book import Book, BookCreate # Переконайтеся, що BookCreate імпортовано

router = APIRouter()

@router.get("", response_model=List[Book])
def get_all_books(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(BookDB).offset(skip).limit(limit).all()

@router.post("", response_model=Book, status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = BookDB(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book