import os
from datetime import datetime, timedelta, timezone
import jwt
from bcrypt import hashpw, gensalt, checkpw
from fastapi import HTTPException, status, Depends
# Змінюємо схему авторизації для Swagger
from fastapi.security import APIKeyHeader
from pydantic_mongo import PydanticObjectId
from models.database import db

SECRET_KEY = "SUPER_SECRET_KEY_DONT_TELL_ANYONE"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Тепер Swagger буде просити просто рядок токена
api_key_scheme = APIKeyHeader(name="Authorization", auto_error=False)

def hash_password(password: str) -> str:
    return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_jwt_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_tokens(user_id: str) -> dict:
    access_token = create_jwt_token({"sub": user_id, "type": "access"}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_jwt_token({"sub": user_id, "type": "refresh"}, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    return {"access_token": access_token, "refresh_token": refresh_token}

# Оновлена функція перевірки токена
async def get_current_user_id(token: str = Depends(api_key_scheme)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
        
    # Swagger іноді передає токен як "Bearer <токен>", відсікаємо префікс якщо він є
    if token.startswith("Bearer ") or token.startswith("bearer "):
        token = token.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
        return user_id
    except jwt.PyJWTError:
        raise credentials_exception