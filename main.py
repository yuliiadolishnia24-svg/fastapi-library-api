from fastapi import FastAPI
from api.endpoints import router as book_router
from api.auth import router as auth_router

# Створюємо екземпляр FastAPI додатка
app = FastAPI(title="Library API with JWT & MongoDB - Lab 6")

# Підключаємо роутер автентифікації з префіксом /auth
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

# Підключаємо роутер книг з префіксом /books
app.include_router(book_router, prefix="/books", tags=["Books"])

@app.get("/")
def read_root():
    return {"message": "API with JWT protection (Access/Refresh flow) running on MongoDB!"}