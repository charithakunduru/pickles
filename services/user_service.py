from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.user import User
from schemas.register import UserRegister
from schemas.login import UserLogin
from schemas.delivery_address import DeliveryAddress
from utils.security import hash_password, verify_password, create_access_token

def register_user(db: Session, user_data: UserRegister) -> User:
    # 1. Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )
    
    # 2. Hash password and create new user
    hashed_pwd = hash_password(user_data.password)
    new_user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        password=hashed_pwd
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def login_user(db: Session, login_data: UserLogin) -> dict:
    # 1. Fetch user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # 2. Create JWT token
    token_data = {
        "sub": user.email,
        "user_id": user.id,
        "role": user.role.value
    }
    access_token = create_access_token(data=token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role.value
        }
    }


def update_delivery_address(db: Session, user_id: int, address_data: DeliveryAddress) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update delivery address fields
    if address_data.first_name:
        user.first_name = address_data.first_name
    user.last_name = address_data.last_name
    user.street_address = address_data.street_address
    user.apartment = address_data.apartment
    user.town_city = address_data.town_city
    user.state = address_data.state
    user.pin_code = address_data.pin_code
    user.phone = address_data.phone
    
    db.commit()
    db.refresh(user)
    return user
