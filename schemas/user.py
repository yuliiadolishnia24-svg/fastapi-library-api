from pydantic import BaseModel, EmailStr, Field
from pydantic_mongo import PydanticObjectId
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    id: PydanticObjectId = Field(..., alias="_id")

    class Config:
        populate_by_name = True