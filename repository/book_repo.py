from sqlalchemy.orm import Session
from models.book_model import BookDB
from uuid import UUID

class BookRepository:
    def get_all(self, db: Session, skip: int = 0, limit: int = 10):
        # Ось тут реалізована Limit-Offset пагінація
        return db.query(BookDB).offset(skip).limit(limit).all()

    def get_by_id(self, db: Session, book_id: UUID):
        return db.query(db.query(BookDB).filter(BookDB.id == book_id).first())

    def create(self, db: Session, book_data: dict):
        db_book = BookDB(**book_data)
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book

    def delete(self, db: Session, book_id: UUID):
        book = db.query(BookDB).filter(BookDB.id == book_id).first()
        if book:
            db.delete(book)
            db.commit()
            return True
        return False