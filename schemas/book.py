from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class BookBase(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    release_year: int
    description: Optional[str] = None
    status: str = "available"

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: UUID

    class Config:
        from_attributes = True