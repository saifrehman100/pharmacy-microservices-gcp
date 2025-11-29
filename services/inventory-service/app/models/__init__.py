"""Database models for Inventory Service."""
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from ..database import Base


class Inventory(Base):
    """Inventory model for tracking product stock levels."""
    __tablename__ = "inventory"

    product_id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer, nullable=False, default=0)
    reorder_level = Column(Integer, nullable=False, default=10)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Inventory(product_id={self.product_id}, quantity={self.quantity})>"
