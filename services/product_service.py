from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
import re
from models.product import PickleProduct
from models.variant import PickleVariant
from schemas.product import ProductCreate
from enums import PickleCategory

def generate_slug(text: str) -> str:
    slug = text.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    return slug

def create_product(db: Session, product_data: ProductCreate) -> PickleProduct:
    # 1. Generate unique slug
    base_slug = product_data.slug or generate_slug(product_data.name)
    slug = base_slug
    counter = 1
    while db.query(PickleProduct).filter(PickleProduct.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    # 2. Create parent PickleProduct
    new_product = PickleProduct(
        name=product_data.name,
        slug=slug,
        category=product_data.category,
        spice_level=product_data.spice_level,
        description=product_data.description,
        ingredients=product_data.ingredients,
        shelf_life_months=product_data.shelf_life_months,
        image_url=product_data.image_url,
        is_available=product_data.is_available,
        is_featured=product_data.is_featured
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    # 3. Create child PickleVariant records
    for v in product_data.variants:
        variant = PickleVariant(
            product_id=new_product.id,
            weight_grams=v.weight_grams,
            weight_label=v.weight_label,
            price=v.price,
            mrp=v.mrp,
            stock_quantity=v.stock_quantity
        )
        db.add(variant)

    db.commit()
    db.refresh(new_product)
    return new_product


def get_all_products(db: Session, category: Optional[PickleCategory] = None) -> List[PickleProduct]:
    query = db.query(PickleProduct)
    if category:
        query = query.filter(PickleProduct.category == category)
    return query.all()


def get_product_by_id(db: Session, product_id: int) -> PickleProduct:
    product = db.query(PickleProduct).filter(PickleProduct.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pickle product with ID {product_id} not found"
        )
    return product


def get_product_by_slug(db: Session, slug: str) -> PickleProduct:
    product = db.query(PickleProduct).filter(PickleProduct.slug == slug).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pickle product '{slug}' not found"
        )
    return product


def delete_product(db: Session, product_id: int):
    product = get_product_by_id(db, product_id)
    db.delete(product)
    db.commit()
    return {"message": f"Product '{product.name}' deleted successfully"}
