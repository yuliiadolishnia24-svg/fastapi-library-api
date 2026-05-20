from pydantic import BaseModel, Field, ConfigDict
from pydantic_mongo import PydanticObjectId
from typing import Optional, List

class BookBase(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    release_year: int
    description: Optional[str] = None
    status: str = "available"

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: PydanticObjectId = Field(..., alias="_id")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True, # Дозволяє мапити _id в id
        json_encoders = {PydanticObjectId: str}
    )