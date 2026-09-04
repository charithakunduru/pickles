from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from models.user import User
from utils.security import get_current_admin
from typing import List, Optional
from database.connection import get_db
from schemas.product import ProductCreate, ProductUpdate, ProductResponse, VariantCreate, VariantUpdate, ProductImageCreate
from enums import PickleCategory
from services.product_service import (
    create_product as create_product_service,
    get_all_products as get_all_products_service,
    get_product_by_id as get_product_by_id_service,
    get_product_by_slug as get_product_by_slug_service,
    update_product as update_product_service,
    delete_product as delete_product_service,
    add_variant_to_product as add_variant_service,
    update_variant as update_variant_service,
    delete_variant as delete_variant_service,
    add_image_to_product as add_image_service,
    delete_product_image as delete_image_service
)

router = APIRouter(prefix="/products", tags=["Pickle Products"])

@router.post("/",response_model=ProductResponse,status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return create_product_service(db, product_data)

@router.get("/", response_model=List[ProductResponse])
def get_products(category: Optional[PickleCategory] = Query(None), db: Session = Depends(get_db)):
    return get_all_products_service(db, category=category)

@router.get("/slug/{slug}", response_model=ProductResponse)
def get_product_by_slug(slug: str, db: Session = Depends(get_db)):
    return get_product_by_slug_service(db, slug)

@router.get("/{product_id}", response_model=ProductResponse)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    return get_product_by_id_service(db, product_id)

@router.post("/{product_id}/variants", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def add_product_variant(
    product_id: int,
    variant_data: VariantCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return add_variant_service(db, product_id, variant_data)

@router.patch("/variants/{variant_id}", response_model=ProductResponse)
def update_product_variant(
    variant_id: int,
    variant_data: VariantUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return update_variant_service(db, variant_id, variant_data)

@router.delete("/variants/{variant_id}", response_model=ProductResponse)
def delete_product_variant(
    variant_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return delete_variant_service(db, variant_id)

@router.post("/{product_id}/images", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def add_product_image(
    product_id: int,
    image_data: ProductImageCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return add_image_service(db, product_id, image_data)

@router.delete("/images/{image_id}", response_model=ProductResponse)
def delete_product_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return delete_image_service(db, image_id)

@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return update_product_service(db, product_id, product_data)

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return delete_product_service(db, product_id)
