# api/endpoints.py
from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
from schemas.book import Book, BookCreate, BookStatus
from services.book_service import BookService

router = APIRouter(prefix="/books", tags=["Books"])
service = BookService()

@router.get("/", response_model=List[Book])
async def get_all_books(
    status: Optional[BookStatus] = None,
    author: Optional[str] = None,
    sort_by: str = Query("title", regex="^(title|release_year)$")
):
    return await service.list_books(status, author, sort_by)

@router.get("/{book_id}", response_model=Book)
async def get_book(book_id: UUID):
    book = await service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
async def add_book(book: BookCreate):
    return await service.create_book(book)

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: UUID):
    await service.delete_book(book_id)
    return None