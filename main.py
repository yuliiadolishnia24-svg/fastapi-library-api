import os
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flasgger import Swagger
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
api = Api(app)

# Налаштовуємо Swagger
swagger = Swagger(app)

# Підключаємо синхронний клієнт PyMongo
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo_admin:password123@localhost:27017")
client = MongoClient(MONGO_URL)
db = client["library_db"]
books_collection = db["books"]

# Допоміжна функція для серіалізації ObjectId від Mongo в звичайний string
def serialize_book(book):
    if book:
        book["id"] = str(book["_id"])
        del book["_id"]
    return book


class BookListResource(Resource):
    def get(self):
        """
        Отримання списку книг з Limit-Offset пагінацією та фільтрацією
        ---
        parameters:
          - name: skip
            in: query
            type: integer
            default: 0
            description: Скільки книг пропустити
          - name: limit
            in: query
            type: integer
            default: 10
            description: Скільки книг повернути
          - name: status
            in: query
            type: string
            description: Фільтр за статусом (available/issued)
          - name: author
            in: query
            type: string
            description: Фільтр за автором
        responses:
          200:
            description: Успішне отримання списку книг
        """
        skip = int(request.args.get("skip", 0))
        limit = int(request.args.get("limit", 10))
        status = request.args.get("status")
        author = request.args.get("author")

        search_filter = {}
        if status:
            search_filter["status"] = status
        if author:
            search_filter["author"] = {"$regex": author, "$options": "i"}

        # Використовуємо синхронний pymongo з лімітами
        cursor = books_collection.find(search_filter).skip(skip).limit(limit)
        books = [serialize_book(book) for book in cursor]
        return jsonify(books)

    def post(self):
        """
        Створення нової книги
        ---
        parameters:
          - name: body
            in: body
            required: true
            schema:
              id: Book
              required:
                - title
                - author
                - release_year
              properties:
                title:
                  type: string
                  default: "Intermezzo"
                author:
                  type: string
                  default: "Михайло Коцюбинський"
                release_year:
                  type: integer
                  default: 1908
                description:
                  type: string
                  default: "Психологічна новела"
                status:
                  type: string
                  default: "available"
        responses:
          201:
            description: Книгу успішно створено
        """
        data = request.get_json()
        
        # Базова валідація
        if not data or "title" not in data or "author" not in data:
            return {"error": "Missing required fields"}, 400

        book_data = {
            "title": data["title"],
            "author": data["author"],
            "release_year": int(data["release_year"]),
            "description": data.get("description", ""),
            "status": data.get("status", "available")
        }

        result = books_collection.insert_one(book_data)
        inserted_book = books_collection.find_one({"_id": result.inserted_id})
        
        return serialize_book(inserted_book), 201


class BookResource(Resource):
    def get(self, book_id):
        """
        Отримання однієї книги за її ID
        ---
        parameters:
          - name: book_id
            in: path
            type: string
            required: true
            description: Унікальний ObjectId книги в Mongo
        responses:
          200:
            description: Книгу знайдено
          44:
            description: Книгу не знайдено
        """
        try:
            book = books_collection.find_one({"_id": ObjectId(book_id)})
        except Exception:
            return {"error": "Invalid ObjectId format"}, 400

        if not book:
            return {"error": "Book not found"}, 404

        return serialize_book(book), 200

    def delete(self, book_id):
        """
        Ідемпотентне видалення книги за ID
        ---
        parameters:
          - name: book_id
            in: path
            type: string
            required: true
            description: Унікальний ObjectId книги
        responses:
          204:
            description: Книгу успішно видалено (або вона вже була видалена)
        """
        try:
            obj_id = ObjectId(book_id)
            books_collection.delete_one({"_id": obj_id})
        except Exception:
            pass # Для ідемпотентності повертаємо 204 навіть при битому ID
            
        return "", 204


# Реєструємо ендпоінти у Flask-RESTful API
api.add_resource(BookListResource, "/books")
api.add_resource(BookResource, "/books/<string:book_id>")

if __name__ == "__main__":
    # Запускаємо сервер на порту 8000, робимо доступним для Docker (0.0.0.0)
    app.run(host="0.0.0.0", port=8000, debug=True)