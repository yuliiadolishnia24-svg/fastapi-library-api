from fastapi import FastAPI
from api.endpoints import router as book_router

app = FastAPI(title="Library API MongoDB - Lab 4-5")

app.include_router(book_router, prefix="/books", tags=["Books"])

@app.get("/")
def read_root():
    return {"message": "API running on MongoDB inside Docker!"}