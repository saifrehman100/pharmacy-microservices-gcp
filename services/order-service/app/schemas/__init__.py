"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from ..models import OrderStatus


class OrderProduct(BaseModel):
    """Schema for product in an order."""
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)


class OrderCreate(BaseModel):
    """Schema for creating an order."""
    user_id: int = Field(..., gt=0)
    products: List[OrderProduct] = Field(..., min_length=1)
    shipping_address: str = Field(..., min_length=10, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status."""
    status: OrderStatus


class OrderResponse(BaseModel):
    """Schema for order response."""
    id: int
    user_id: int
    products: List[OrderProduct]
    total_amount: float
    status: OrderStatus
    shipping_address: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
