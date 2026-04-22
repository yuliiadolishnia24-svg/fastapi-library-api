from sqlalchemy import Column, String, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .database import Base
from schemas.book import BookStatus

class BookDB(Base):
    __tablename__ = "books"

    # Стовпці нашої таблиці в базі даних
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    description = Column(String, nullable=True)
    release_year = Column(Integer, nullable=False)
    
    # Використовуємо статус із наших схем
    status = Column(SQLEnum(BookStatus), default=BookStatus.AVAILABLE)