from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database.connection import get_db
from schemas.register import UserRegister
from schemas.login import UserLogin
from services.user_service import register_user, login_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    user = register_user(db, user_data)
    return {
        "message": "User registered successfully",
        "user_id": user.id,
        "email": user.email
    }

@router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    return login_user(db, login_data)
