from fastapi import FastAPI
from api.endpoints import router as book_router
from models.database import engine, Base

# Створення таблиць у library.db
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Library API")

# Підключаємо роутер з префіксом /books
app.include_router(book_router, prefix="/books", tags=["Books"])

@app.get("/")
def root():
    return {"message": "Welcome to Library API"}