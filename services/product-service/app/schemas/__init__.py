"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    """Base product schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=100)
    requires_prescription: bool = False
    manufacturer: Optional[str] = Field(None, max_length=255)
    stock_keeping_unit: str = Field(..., min_length=1, max_length=100)


class ProductCreate(ProductBase):
    """Schema for creating a product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    requires_prescription: Optional[bool] = None
    manufacturer: Optional[str] = Field(None, max_length=255)
    stock_keeping_unit: Optional[str] = Field(None, min_length=1, max_length=100)


class ProductResponse(ProductBase):
    """Schema for product response."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaginatedProductResponse(BaseModel):
    """Schema for paginated product list."""
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
