from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from typing import List, Optional
import re
from models.product import PickleProduct
from models.variant import PickleVariant
from models.product_image import PickleProductImage
from schemas.product import ProductCreate, ProductUpdate, VariantCreate, VariantUpdate, ProductImageCreate, ProductImageUpdate
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

    # 3. Create child PickleVariant records
    for v in product_data.variants:
        variant = PickleVariant(
            weight_grams=v.weight_grams,
            weight_label=v.weight_label,
            price=v.price,
            mrp=v.mrp,
            stock_quantity=v.stock_quantity
        )
        new_product.variants.append(variant)

    # 4. Create child PickleProductImage records
    if product_data.images:
        for img in product_data.images:
            image_record = PickleProductImage(
                image_url=img.image_url,
                is_primary=img.is_primary,
                display_order=img.display_order
            )
            new_product.images.append(image_record)

    db.add(new_product)
    db.commit()
    return get_product_by_id(db, new_product.id)


def get_all_products(db: Session, category: Optional[PickleCategory] = None) -> List[PickleProduct]:
    query = db.query(PickleProduct).options(
        joinedload(PickleProduct.variants),
        joinedload(PickleProduct.images)
    )
    if category:
        query = query.filter(PickleProduct.category == category)
    return query.all()


def get_product_by_id(db: Session, product_id: int) -> PickleProduct:
    product = db.query(PickleProduct).options(
        joinedload(PickleProduct.variants),
        joinedload(PickleProduct.images)
    ).filter(PickleProduct.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pickle product with ID {product_id} not found"
        )
    return product


def get_product_by_slug(db: Session, slug: str) -> PickleProduct:
    product = db.query(PickleProduct).options(
        joinedload(PickleProduct.variants),
        joinedload(PickleProduct.images)
    ).filter(PickleProduct.slug == slug).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pickle product '{slug}' not found"
        )
    return product


def update_product(db: Session, product_id: int, product_data: ProductUpdate) -> PickleProduct:
    product = get_product_by_id(db, product_id)
    update_dict = product_data.model_dump(exclude_unset=True)

    variants_data = update_dict.pop("variants", None)
    images_data = update_dict.pop("images", None)

    if "name" in update_dict and "slug" not in update_dict:
        base_slug = generate_slug(update_dict["name"])
        slug = base_slug
        counter = 1
        while db.query(PickleProduct).filter(PickleProduct.slug == slug, PickleProduct.id != product_id).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        product.slug = slug
    elif "slug" in update_dict and update_dict["slug"]:
        slug = update_dict["slug"]
        existing = db.query(PickleProduct).filter(PickleProduct.slug == slug, PickleProduct.id != product_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Slug '{slug}' is already in use by another product"
            )

    for key, value in update_dict.items():
        setattr(product, key, value)

    if variants_data is not None:
        for v_data in variants_data:
            v_id = v_data.get("id")
            if v_id:
                variant = db.query(PickleVariant).filter(
                    PickleVariant.id == v_id,
                    PickleVariant.product_id == product_id
                ).first()
                if variant:
                    for vk, vv in v_data.items():
                        if vk != "id" and vv is not None:
                            setattr(variant, vk, vv)
            else:
                new_variant = PickleVariant(
                    product_id=product_id,
                    weight_grams=v_data.get("weight_grams", 0),
                    weight_label=v_data.get("weight_label", ""),
                    price=v_data.get("price", 0.0),
                    mrp=v_data.get("mrp"),
                    stock_quantity=v_data.get("stock_quantity", 0)
                )
                db.add(new_variant)

    if images_data is not None:
        for img_data in images_data:
            img_id = img_data.get("id")
            if img_id:
                image_record = db.query(PickleProductImage).filter(
                    PickleProductImage.id == img_id,
                    PickleProductImage.product_id == product_id
                ).first()
                if image_record:
                    for ik, iv in img_data.items():
                        if ik != "id" and iv is not None:
                            setattr(image_record, ik, iv)
            else:
                new_image = PickleProductImage(
                    product_id=product_id,
                    image_url=img_data.get("image_url", ""),
                    is_primary=img_data.get("is_primary", False),
                    display_order=img_data.get("display_order", 0)
                )
                db.add(new_image)

    db.commit()
    return get_product_by_id(db, product_id)


def delete_product(db: Session, product_id: int):
    product = get_product_by_id(db, product_id)
    db.delete(product)
    db.commit()
    return {"message": f"Product '{product.name}' deleted successfully"}


def add_variant_to_product(db: Session, product_id: int, variant_data: VariantCreate) -> PickleProduct:
    product = get_product_by_id(db, product_id)
    new_variant = PickleVariant(
        product_id=product.id,
        weight_grams=variant_data.weight_grams,
        weight_label=variant_data.weight_label,
        price=variant_data.price,
        mrp=variant_data.mrp,
        stock_quantity=variant_data.stock_quantity
    )
    db.add(new_variant)
    db.commit()
    return get_product_by_id(db, product_id)


def delete_variant(db: Session, variant_id: int) -> PickleProduct:
    variant = db.query(PickleVariant).filter(PickleVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variant with ID {variant_id} not found"
        )
    product_id = variant.product_id
    db.delete(variant)
    db.commit()
    return get_product_by_id(db, product_id)


def update_variant(db: Session, variant_id: int, variant_data: VariantUpdate) -> PickleProduct:
    variant = db.query(PickleVariant).filter(PickleVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variant with ID {variant_id} not found"
        )
    update_dict = variant_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if key != "id" and value is not None:
            setattr(variant, key, value)

    db.commit()
    return get_product_by_id(db, variant.product_id)


def add_image_to_product(db: Session, product_id: int, image_data: ProductImageCreate) -> PickleProduct:
    product = get_product_by_id(db, product_id)
    new_image = PickleProductImage(
        product_id=product.id,
        image_url=image_data.image_url,
        is_primary=image_data.is_primary,
        display_order=image_data.display_order
    )
    db.add(new_image)
    db.commit()
    return get_product_by_id(db, product_id)


def delete_product_image(db: Session, image_id: int) -> PickleProduct:
    image_record = db.query(PickleProductImage).filter(PickleProductImage.id == image_id).first()
    if not image_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product image with ID {image_id} not found"
        )
    product_id = image_record.product_id
    db.delete(image_record)
    db.commit()
    return get_product_by_id(db, product_id)
