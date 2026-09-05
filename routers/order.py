from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List
from database.connection import get_db
from models.user import User
from schemas.order import OrderCreate, OrderResponse
from enums import OrderStatus
from utils.security import get_current_user, get_current_admin
from services.order_service import (
    create_order as create_order_service,
    get_user_orders as get_user_orders_service,
    get_order_by_id as get_order_by_id_service,
    update_order_status as update_order_status_service
)

router = APIRouter(prefix="/orders", tags=["Orders & Checkout"])

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def place_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_order_service(db, current_user, order_data)

@router.get("/my-orders", response_model=List[OrderResponse])
def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_user_orders_service(db, current_user.id)

@router.get("/{order_id}", response_model=OrderResponse)
def get_order_details(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_order_by_id_service(db, order_id, current_user)

@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_status(
    order_id: int,
    status_enum: OrderStatus = Query(...),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return update_order_status_service(db, order_id, status_enum)
