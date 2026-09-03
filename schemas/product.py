from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enums import PickleCategory, SpiceLevel

class VariantBase(BaseModel):
    weight_grams: int
    weight_label: str
    price: float
    mrp: Optional[float] = None
    stock_quantity: int = 0

class VariantCreate(VariantBase):
    pass

class VariantResponse(VariantBase):
    id: int
    product_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str
    category: PickleCategory
    spice_level: SpiceLevel = SpiceLevel.MEDIUM
    description: Optional[str] = None
    ingredients: Optional[str] = None
    shelf_life_months: Optional[int] = 6
    image_url: Optional[str] = None
    is_available: bool = True
    is_featured: bool = False

class ProductCreate(ProductBase):
    slug: Optional[str] = None  # Auto-generated if not provided
    variants: List[VariantCreate]

class ProductResponse(ProductBase):
    id: int
    slug: str
    created_at: datetime
    updated_at: datetime
    variants: List[VariantResponse] = []

    class Config:
        from_attributes = True
