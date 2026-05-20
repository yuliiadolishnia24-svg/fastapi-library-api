import os
import motor.motor_asyncio

# Беремо URL з енвайронменту Docker, або локальний за замовчуванням
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo_admin:password123@localhost:27017")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client["library_db"]

# Функція (Dependency) для отримання доступу до колекції книг
def get_books_collection():
    return db["books"]