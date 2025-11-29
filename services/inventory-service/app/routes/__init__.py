"""API routes for Inventory Service."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Inventory
from ..schemas import (
    InventoryCreate,
    InventoryResponse,
    InventoryAdjust,
    LowStockAlert
)
from ..inventory_service import check_low_stock

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("/{product_id}", response_model=InventoryResponse)
async def get_inventory(product_id: int, db: Session = Depends(get_db)):
    """Get inventory level for a specific product."""
    inventory = db.query(Inventory).filter(
        Inventory.product_id == product_id
    ).first()

    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory record for product {product_id} not found"
        )

    return inventory


@router.post("", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory(
    inventory_data: InventoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new inventory record."""
    # Check if inventory already exists
    existing = db.query(Inventory).filter(
        Inventory.product_id == inventory_data.product_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Inventory for product {inventory_data.product_id} already exists"
        )

    # Create new inventory record
    new_inventory = Inventory(**inventory_data.model_dump())
    db.add(new_inventory)
    db.commit()
    db.refresh(new_inventory)

    return new_inventory


@router.put("/{product_id}/adjust", response_model=InventoryResponse)
async def adjust_inventory(
    product_id: int,
    adjustment_data: InventoryAdjust,
    db: Session = Depends(get_db)
):
    """Adjust inventory quantity (add or remove stock)."""
    inventory = db.query(Inventory).filter(
        Inventory.product_id == product_id
    ).first()

    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory record for product {product_id} not found"
        )

    # Adjust quantity
    new_quantity = inventory.quantity + adjustment_data.adjustment

    if new_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Adjustment would result in negative inventory. "
                   f"Current: {inventory.quantity}, Adjustment: {adjustment_data.adjustment}"
        )

    inventory.quantity = new_quantity
    db.commit()
    db.refresh(inventory)

    return inventory


@router.get("/low-stock", response_model=List[LowStockAlert])
async def get_low_stock_items(db: Session = Depends(get_db)):
    """Get all products with low stock levels."""
    low_stock_items = check_low_stock(db)

    alerts = [
        LowStockAlert(
            product_id=item.product_id,
            current_quantity=item.quantity,
            reorder_level=item.reorder_level,
            shortage=item.reorder_level - item.quantity
        )
        for item in low_stock_items
    ]

    return alerts


@router.get("", response_model=List[InventoryResponse])
async def list_all_inventory(db: Session = Depends(get_db)):
    """List all inventory records."""
    inventory_items = db.query(Inventory).order_by(Inventory.product_id).all()
    return inventory_items
