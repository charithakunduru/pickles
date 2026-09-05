from pydantic import BaseModel, Field,EmailStr
from typing import List, Optional
from datetime import datetime
from enums import OrderStatus, PaymentStatus, PaymentMethod
from schemas.delivery_address import DeliveryAddress

class OrderItemCreate(BaseModel):
    product_id: int
    variant_id: int
    quantity: int = Field(..., gt=0, description="Quantity must be at least 1")

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    payment_method: PaymentMethod = PaymentMethod.COD
    customer_email: EmailStr
    shipping_address: Optional[DeliveryAddress] = None  # If null, uses user profile address


class OrderItemResponse(BaseModel):
    id: int
    product_id: Optional[int]
    variant_id: Optional[int]
    product_name: str
    weight_label: str
    unit_price: float
    quantity: int
    total_price: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    order_number: str
    user_id: Optional[int]
    customer_email: EmailStr
    total_amount: float
    status: OrderStatus
    payment_status: PaymentStatus
    payment_method: PaymentMethod

    shipping_first_name: str
    shipping_last_name: str
    shipping_street_address: str
    shipping_apartment: Optional[str]
    shipping_town_city: str
    shipping_state: str
    shipping_pin_code: str
    shipping_phone: str

    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True
