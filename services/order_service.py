import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from models.user import User, UserRole
from models.product import PickleProduct
from models.variant import PickleVariant
from models.order import Order, OrderItem
from schemas.order import OrderCreate
from enums import OrderStatus, PaymentStatus

def generate_order_number() -> str:
    return f"PICKLE-{uuid.uuid4().hex[:8].upper()}"

def create_order(db: Session, order_data: OrderCreate, user: User = None) -> Order:
    # 1. Validate shipping address
    address = order_data.shipping_address

    if address:
        shipping_first_name = address.first_name
        shipping_last_name = address.last_name
        shipping_street_address = address.street_address
        shipping_apartment = address.apartment
        shipping_town_city = address.town_city
        shipping_state = address.state
        shipping_pin_code = address.pin_code
        shipping_phone = address.phone

    elif user:
        # Logged-in user: use saved profile address
        shipping_first_name = user.first_name
        shipping_last_name = user.last_name
        shipping_street_address = user.street_address
        shipping_apartment = user.apartment
        shipping_town_city = user.town_city
        shipping_state = user.state
        shipping_pin_code = user.pin_code
        shipping_phone = user.phone

    else:
        # Guest checkout must provide shipping address
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Shipping address is required for guest checkout."
        )

    if not shipping_street_address or not shipping_town_city or not shipping_pin_code or not shipping_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incomplete shipping address. Please provide all required address details."
        )

    # 2. Process items, validate product & variant IDs, check stock & calculate total
    order_items_to_create = []
    grand_total = 0.0

    for item_data in order_data.items:
        # Validate Product exists
        product = db.query(PickleProduct).filter(PickleProduct.id == item_data.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product ID {item_data.product_id} not found."
            )

        # Validate Variant exists
        variant = db.query(PickleVariant).filter(PickleVariant.id == item_data.variant_id).first()
        if not variant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product variant ID {item_data.variant_id} not found."
            )

        # Validate Variant belongs to specified Product
        if variant.product_id != item_data.product_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Variant ID {item_data.variant_id} does not belong to Product '{product.name}' (ID: {item_data.product_id})."
            )
        
        if not product.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{product.name}' is currently unavailable."
            )

        if variant.stock_quantity < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for '{product.name} ({variant.weight_label})'. Available: {variant.stock_quantity}, Requested: {item_data.quantity}"
            )

        # Calculate line item price
        unit_price = variant.price
        total_price = unit_price * item_data.quantity
        grand_total += total_price

        # Decrement stock
        variant.stock_quantity -= item_data.quantity

        # Prepare OrderItem
        order_items_to_create.append({
            "product_id": product.id,
            "variant_id": variant.id,
            "product_name": product.name,
            "weight_label": variant.weight_label,
            "unit_price": unit_price,
            "quantity": item_data.quantity,
            "total_price": total_price
        })

    # 3. Create Order Parent Record
    new_order = Order(
        order_number=generate_order_number(),
        customer_email=order_data.customer_email,
        user_id=user.id if user else None,
        total_amount=grand_total,
        status=OrderStatus.PENDING,
        payment_status=PaymentStatus.PENDING,
        payment_method=order_data.payment_method,
        shipping_first_name=shipping_first_name,
        shipping_last_name=shipping_last_name,
        shipping_street_address=shipping_street_address,
        shipping_apartment=shipping_apartment,
        shipping_town_city=shipping_town_city,
        shipping_state=shipping_state,
        shipping_pin_code=shipping_pin_code,
        shipping_phone=shipping_phone
    )

    db.add(new_order)
    db.flush()

    # 4. Create OrderItems
    for item in order_items_to_create:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item["product_id"],
            variant_id=item["variant_id"],
            product_name=item["product_name"],
            weight_label=item["weight_label"],
            unit_price=item["unit_price"],
            quantity=item["quantity"],
            total_price=item["total_price"]
        )
        db.add(order_item)

    db.commit()
    db.refresh(new_order)
    return new_order


def get_user_orders(db: Session, user_id: int) -> List[Order]:
    return db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()


def get_order_by_id(db: Session, order_id: int, current_user: User) -> Order:
    query = db.query(Order).filter(Order.id == order_id)
    if current_user.role != UserRole.ROLE_ADMIN:
        query = query.filter(Order.user_id == current_user.id)
    
    order = query.first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order ID {order_id} not found."
        )
    return order


def update_order_status(db: Session, order_id: int, new_status: OrderStatus) -> Order:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order ID {order_id} not found."
        )
    order.status = new_status
    if new_status == OrderStatus.DELIVERED:
        order.payment_status = PaymentStatus.PAID

    db.commit()
    db.refresh(order)
    return order
