# services/book_service.py
from uuid import UUID
from repository.book_repo import BookRepository
from schemas.book import Book, BookCreate, BookStatus
from typing import Optional, List

class BookService:
    def __init__(self):
        self.repo = BookRepository()

    async def list_books(self, status: Optional[BookStatus] = None, author: Optional[str] = None, sort_by: str = "title"):
        books = await self.repo.get_all()
        
        # Фільтрація
        filtered_books = books
        if status:
            filtered_books = [b for b in filtered_books if b["status"] == status]
        if author:
            filtered_books = [b for b in filtered_books if author.lower() in b["author"].lower()]
        
        # Сортування (робимо копію, щоб не псувати оригінал)
        result = list(filtered_books)
        if sort_by == "release_year":
            result.sort(key=lambda x: x["release_year"])
        else:
            result.sort(key=lambda x: x["title"].lower())
            
        return result

    async def get_book(self, book_id: UUID):
        return await self.repo.get_by_id(book_id)

    async def create_book(self, book_in: BookCreate):
        new_book = Book(**book_in.model_dump())
        return await self.repo.add(new_book)

    async def delete_book(self, book_id: UUID):
        return await self.repo.delete(book_id)