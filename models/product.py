from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from database.connection import Base
from enums import PickleCategory, SpiceLevel

class PickleProduct(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), nullable=False, index=True)
    slug = Column(String(150), unique=True, index=True, nullable=False)
    category = Column(SQLEnum(PickleCategory), nullable=False, index=True)
    spice_level = Column(SQLEnum(SpiceLevel), default=SpiceLevel.MEDIUM, nullable=False)
    description = Column(Text, nullable=True)
    ingredients = Column(Text, nullable=True)
    shelf_life_months = Column(Integer, default=6, nullable=False)
    image_url = Column(String(255), nullable=True)
    is_available = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    variants = relationship("PickleVariant", back_populates="product", cascade="all, delete-orphan", lazy="joined")
    images = relationship("PickleProductImage", back_populates="product", cascade="all, delete-orphan", lazy="joined")

    def __repr__(self):
        return f"<PickleProduct(id={self.id}, name='{self.name}', category='{self.category}')>"
