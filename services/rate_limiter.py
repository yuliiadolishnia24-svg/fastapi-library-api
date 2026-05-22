import os
import time
from fastapi import Request, HTTPException, status
import redis.asyncio as redis

# Отримуємо URL з конфігу докера, або використовуємо localhost для локальних тестів
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Вимоги ЛР7: 2 для анонімів, 10 для авторизованих користувачів на 60 секунд
RATE_LIMITS = {
    "anonymous": (2, 60),
    "authenticated": (10, 60)
}

async def check_rate_limit(request: Request, user_id: str | None = None):
    # Визначаємо identity користувача (ID або IP-адреса)
    identity = user_id or request.client.host
    
    # Визначаємо тип ліміту
    limit_type = "authenticated" if user_id else "anonymous"
    limit, period = RATE_LIMITS[limit_type]
    
    key = f"rate_limit_{identity}"
    now = time.time()
    window_start = now - period
    
    # Логіка Sliding Time Window через Sorted Sets
    # 1. Видаляємо всі записи, які вилетіли за межі нашого часового вікна (старіші за 60 сек)
    await redis_client.zremrangebyscore(key, min=0, max=window_start)
    
    # 2. Рахуємо кількість запитів користувача в поточному вікні
    request_count = await redis_client.zcard(key)
    
    # 3. Перевіряємо, чи не перевищено ліміт
    if request_count >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later."
        )
    
    # 4. Додаємо поточний запит у ZSET (значення та скор — поточний unix timestamp)
    # Використовуємо унікальну строку "now" з мікросекундами, щоб уникнути колізій при швидких запитах
    await redis_client.zadd(key, {f"{now}": now})
    
    # 5. Оновлюємо TTL ключа, щоб він не висів у пам'яті вічно
    await redis_client.expire(key, period)