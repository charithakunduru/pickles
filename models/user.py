from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Enum as SQLEnum, DateTime
from database.connection import Base
from enums import UserRole

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    street_address = Column(Text, nullable=True)
    apartment = Column(String(100), nullable=True)
    town_city = Column(String(100), nullable=True)
    pin_code = Column(String(20), nullable=True)
    state = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.ROLE_USER, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
