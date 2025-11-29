"""API routes for Order Service."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Order, OrderStatus
from ..schemas import OrderCreate, OrderResponse, OrderStatusUpdate
from ..pubsub import get_publisher

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order and publish event to Pub/Sub."""
    # Calculate total amount
    total_amount = sum(
        product.quantity * product.price
        for product in order_data.products
    )

    # Create order
    new_order = Order(
        user_id=order_data.user_id,
        products=[p.model_dump() for p in order_data.products],
        total_amount=total_amount,
        shipping_address=order_data.shipping_address,
        notes=order_data.notes,
        status=OrderStatus.PENDING
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Publish order created event to Pub/Sub
    publisher = get_publisher()
    await publisher.publish_order_created({
        "id": new_order.id,
        "user_id": new_order.user_id,
        "products": new_order.products,
        "total_amount": new_order.total_amount,
        "created_at": new_order.created_at
    })

    return new_order


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get a specific order by ID."""
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found"
        )

    return order


@router.get("/user/{user_id}", response_model=List[OrderResponse])
async def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    """Get all orders for a specific user."""
    orders = db.query(Order).filter(Order.user_id == user_id)\
        .order_by(Order.created_at.desc()).all()

    return orders


@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db)
):
    """Update order status and publish event."""
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found"
        )

    # Store old status for event
    old_status = order.status

    # Update status
    order.status = status_update.status
    db.commit()
    db.refresh(order)

    # Publish status change event
    if old_status != status_update.status:
        publisher = get_publisher()
        await publisher.publish_order_status_changed(
            order_id=order.id,
            old_status=old_status.value,
            new_status=status_update.status.value
        )

    return order
