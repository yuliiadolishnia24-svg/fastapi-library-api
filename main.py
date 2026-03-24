# main.py
from fastapi import FastAPI
from api.endpoints import router

app = FastAPI(title="Library API")

# Підключаємо наші маршрути
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Welcome to Library API. Go to /docs for Swagger UI."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)