# schemas/book.py
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from enum import Enum
from typing import Optional

class BookStatus(str, Enum):
    AVAILABLE = "available"
    BORROWED = "borrowed"

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    release_year: int = Field(..., gt=0)
    status: BookStatus = BookStatus.AVAILABLE

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: UUID = Field(default_factory=uuid4)