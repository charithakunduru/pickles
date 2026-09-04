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


class ProductImageBase(BaseModel):
    image_url: str
    is_primary: bool = False
    display_order: int = 0

class ProductImageCreate(ProductImageBase):
    pass

class ProductImageResponse(ProductImageBase):
    id: int
    product_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProductImageUpdate(BaseModel):
    id: Optional[int] = None
    image_url: Optional[str] = None
    is_primary: Optional[bool] = None
    display_order: Optional[int] = None


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
    images: Optional[List[ProductImageCreate]] = []

class VariantUpdate(BaseModel):
    id: Optional[int] = None
    weight_grams: Optional[int] = None
    weight_label: Optional[str] = None
    price: Optional[float] = None
    mrp: Optional[float] = None
    stock_quantity: Optional[int] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    category: Optional[PickleCategory] = None
    spice_level: Optional[SpiceLevel] = None
    description: Optional[str] = None
    ingredients: Optional[str] = None
    shelf_life_months: Optional[int] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None
    is_featured: Optional[bool] = None
    variants: Optional[List[VariantUpdate]] = None
    images: Optional[List[ProductImageUpdate]] = None

class ProductResponse(ProductBase):
    id: int
    slug: str
    created_at: datetime
    updated_at: datetime
    variants: List[VariantResponse] = []
    images: List[ProductImageResponse] = []

    class Config:
        from_attributes = True
