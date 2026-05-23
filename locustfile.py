import uuid
from locust import HttpUser, task, between

class LibraryUser(HttpUser):
    # Пауза між запитами від 1 до 2 секунд
    wait_time = between(1, 2)

    @task
    def create_book(self):
        # Генеруємо унікальну назву книги, щоб тести були різноманітними
        unique_id = uuid.uuid4().hex[:6]
        
        payload = {
            "title": f"Book {unique_id}",
            "author": "John Doe"
        }
        
        # Відправляємо POST-запит на створення книги в наш мок-сервер
        self.client.post(
            "/books", 
            json=payload, 
            name="Додавання нової книги"
        )