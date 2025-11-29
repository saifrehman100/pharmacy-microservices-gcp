"""Database models for Product Service."""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from ..database import Base


class Product(Base):
    """Product model for pharmacy items."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    requires_prescription = Column(Boolean, default=False)
    manufacturer = Column(String(255))
    stock_keeping_unit = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', sku='{self.stock_keeping_unit}')>"
