"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from datetime import datetime


class InventoryBase(BaseModel):
    """Base inventory schema."""
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=0)
    reorder_level: int = Field(default=10, ge=0)


class InventoryCreate(InventoryBase):
    """Schema for creating inventory record."""
    pass


class InventoryAdjust(BaseModel):
    """Schema for adjusting inventory quantity."""
    adjustment: int = Field(..., description="Positive to add, negative to remove")
    reason: str = Field(default="Manual adjustment")


class InventoryResponse(InventoryBase):
    """Schema for inventory response."""
    last_updated: datetime

    class Config:
        from_attributes = True


class LowStockAlert(BaseModel):
    """Schema for low stock alerts."""
    product_id: int
    current_quantity: int
    reorder_level: int
    shortage: int
