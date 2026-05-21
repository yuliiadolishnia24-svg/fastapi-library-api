from fastapi import APIRouter, HTTPException, status, Depends
from models.database import db
from schemas.user import UserCreate, UserResponse
from schemas.token import TokenResponse, RefreshTokenRequest
from services.auth import hash_password, verify_password, create_tokens, SECRET_KEY, ALGORITHM
import jwt

router = APIRouter()
users_collection = db["users"]

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_in: UserCreate):
    existing_user = await users_collection.find_one({"email": user_in.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_dict = {
        "email": user_in.email,
        "hashed_password": hash_password(user_in.password),
        "refresh_token": None
    }
    result = await users_collection.insert_one(user_dict)
    inserted_user = await users_collection.find_one({"_id": result.inserted_id})
    return inserted_user


@router.post("/login", response_model=TokenResponse)
async def login(user_in: UserCreate):
    user = await users_collection.find_one({"email": user_in.email})
    if not user or not verify_password(user_in.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    tokens = create_tokens(str(user["_id"]))
    
    # Зберігаємо refresh token в базу даних користувача
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"refresh_token": tokens["refresh_token"]}}
    )
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(body: RefreshTokenRequest):
    try:
        payload = jwt.decode(body.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    # Шукаємо користувача і звіряємо, чи цей токен збігається з тим, що в базі
    from bson import ObjectId
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user or user.get("refresh_token") != body.refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token revoked or invalid")
    
    # ГExecutable нові токени
    new_tokens = create_tokens(user_id)
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"refresh_token": new_tokens["refresh_token"]}}
    )
    return new_tokens