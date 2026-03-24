# repository/book_repo.py
from uuid import UUID
from models.data import books_db
from schemas.book import Book

class BookRepository:
    async def get_all(self):
        return books_db

    async def get_by_id(self, book_id: UUID):
        return next((b for b in books_db if b["id"] == book_id), None)

    async def add(self, book_data: Book):
        books_db.append(book_data.model_dump())
        return book_data

    async def delete(self, book_id: UUID):
        global books_db
        index = next((i for i, b in enumerate(books_db) if b["id"] == book_id), None)
        if index is not None:
            books_db.pop(index)
            return True
        return False