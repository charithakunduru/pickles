from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.connection import get_db
from schemas.product import ProductCreate, ProductResponse
from enums import PickleCategory
from services.product_service import (
    create_product as create_product_service,
    get_all_products as get_all_products_service,
    get_product_by_id as get_product_by_id_service,
    get_product_by_slug as get_product_by_slug_service,
    delete_product as delete_product_service
)

router = APIRouter(prefix="/products", tags=["Pickle Products"])

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
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

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    return delete_product_service(db, product_id)
