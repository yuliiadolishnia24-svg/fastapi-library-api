import uuid
from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from models.database import Base

class BookDB(Base):
    __tablename__ = "books"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, index=True, nullable=False)
    release_year = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, index=True, default="available") # available / issued