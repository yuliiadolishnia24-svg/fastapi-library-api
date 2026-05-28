import os
import motor.motor_asyncio

# Локальний URL за замовчуванням без пароля, або з Docker-оточення
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client["library_db"]

# Функція (Dependency) для отримання доступу до колекції книг
def get_books_collection():
    return db["books"]