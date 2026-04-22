# Використовуємо легку версію Python
FROM python:3.12-slim

# Робоча папка всередині контейнера
WORKDIR /app

# Встановлюємо системні бібліотеки для PostgreSQL
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Копіюємо список бібліотек і встановлюємо їх
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь наш код у контейнер
COPY . .

# Команда для запуску сервера
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]