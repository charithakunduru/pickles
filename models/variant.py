from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base

class PickleVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    weight_grams = Column(Integer, nullable=False)  # e.g., 250, 500, 1000
    weight_label = Column(String(50), nullable=False)  # e.g., "250g", "500g", "1 kg"
    price = Column(Float, nullable=False)
    mrp = Column(Float, nullable=True)
    stock_quantity = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    product = relationship("PickleProduct", back_populates="variants")

    def __repr__(self):
        return f"<PickleVariant(id={self.id}, label='{self.weight_label}', price={self.price})>"
