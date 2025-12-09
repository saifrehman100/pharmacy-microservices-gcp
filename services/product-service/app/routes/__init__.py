"""API routes for Product Service."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
import math

from ..database import get_db
from ..models import Product
from ..schemas import ProductCreate, ProductUpdate, ProductResponse, PaginatedProductResponse
from ..config import settings

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=PaginatedProductResponse)
async def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(
        settings.default_page_size,
        ge=1,
        le=settings.max_page_size,
        description="Items per page"
    ),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    """List all products with pagination and optional filtering"""
    # Build query
    query = db.query(Product)

    # Apply filters
    if category:
        query = query.filter(Product.category == category)

    # Get total count
    total = query.count()

    # Calculate pagination
    total_pages = math.ceil(total / page_size)
    skip = (page - 1) * page_size

    # Get paginated results
    products = query.order_by(Product.created_at.desc()).offset(skip).limit(page_size).all()

    return {
        "items": products,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@router.get("/search", response_model=list[ProductResponse])
async def search_products(
    name: Optional[str] = Query(None, description="Search by product name"),
    manufacturer: Optional[str] = Query(None, description="Search by manufacturer"),
    db: Session = Depends(get_db)
):
    """Search products by name or manufacturer."""
    query = db.query(Product)

    if name:
        query = query.filter(Product.name.ilike(f"%{name}%"))

    if manufacturer:
        query = query.filter(Product.manufacturer.ilike(f"%{manufacturer}%"))

    products = query.order_by(Product.name).limit(50).all()
    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID."""
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )

    return product


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product."""
    # Check if SKU already exists
    existing_product = db.query(Product).filter(
        Product.stock_keeping_unit == product_data.stock_keeping_unit
    ).first()

    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with SKU '{product_data.stock_keeping_unit}' already exists"
        )

    # Create new product
    new_product = Product(**product_data.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing product."""
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )

    # Check SKU uniqueness if being updated
    if product_data.stock_keeping_unit:
        existing_sku = db.query(Product).filter(
            Product.stock_keeping_unit == product_data.stock_keeping_unit,
            Product.id != product_id
        ).first()

        if existing_sku:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with SKU '{product_data.stock_keeping_unit}' already exists"
            )

    # Update product fields
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product."""
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )

    db.delete(product)
    db.commit()

    return None
