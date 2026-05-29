import os
import motor.motor_asyncio

# Локальний URL без паролів за замовчуванням, або з докера
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client["library_db"]

# Ця функція ОБОВ'ЯЗКОВО потрібна для endpoints.py
def get_books_collection():
    return db["books"]