from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base
from enums import OrderStatus, PaymentStatus, PaymentMethod

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    customer_email = Column(String(150), nullable=True)
    
    total_amount = Column(Float, nullable=False)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), default=PaymentMethod.COD, nullable=False)

    # Shipping Address Snapshot
    shipping_first_name = Column(String(100), nullable=False)
    shipping_last_name = Column(String(100), nullable=False)
    shipping_street_address = Column(Text, nullable=False)
    shipping_apartment = Column(String(100), nullable=True)
    shipping_town_city = Column(String(100), nullable=False)
    shipping_state = Column(String(100), nullable=False)
    shipping_pin_code = Column(String(20), nullable=False)
    shipping_phone = Column(String(20), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order(id={self.id}, order_number='{self.order_number}', total={self.total_amount})>"


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True)

    # Snapshots to preserve historical accuracy
    product_name = Column(String(150), nullable=False)
    weight_label = Column(String(50), nullable=False)
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("PickleProduct")
    variant = relationship("PickleVariant")

    def __repr__(self):
        return f"<OrderItem(id={self.id}, name='{self.product_name}', qty={self.quantity})>"
