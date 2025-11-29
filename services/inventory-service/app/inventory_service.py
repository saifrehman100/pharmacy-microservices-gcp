"""Business logic for inventory management."""
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session

from .models import Inventory
from .config import settings

logger = logging.getLogger(__name__)


def process_order_event(db: Session, event_data: Dict[str, Any]) -> None:
    """
    Process order created event and update inventory.

    Args:
        db: Database session
        event_data: Order event data from Pub/Sub
    """
    order_id = event_data.get("order_id")
    products = event_data.get("products", [])

    logger.info(f"Processing order {order_id} with {len(products)} products")

    for product in products:
        product_id = product.get("product_id")
        quantity = product.get("quantity")

        if not product_id or not quantity:
            logger.warning(f"Invalid product data in order {order_id}: {product}")
            continue

        # Get or create inventory record
        inventory = db.query(Inventory).filter(
            Inventory.product_id == product_id
        ).first()

        if not inventory:
            # Create new inventory record if it doesn't exist
            inventory = Inventory(
                product_id=product_id,
                quantity=0,
                reorder_level=settings.low_stock_threshold
            )
            db.add(inventory)
            logger.info(f"Created new inventory record for product {product_id}")

        # Decrease inventory quantity
        old_quantity = inventory.quantity
        inventory.quantity = max(0, inventory.quantity - quantity)

        logger.info(
            f"Updated inventory for product {product_id}: "
            f"{old_quantity} -> {inventory.quantity} (ordered: {quantity})"
        )

        # Check for low stock
        if inventory.quantity <= inventory.reorder_level:
            logger.warning(
                f"LOW STOCK ALERT: Product {product_id} has {inventory.quantity} units "
                f"(reorder level: {inventory.reorder_level})"
            )

    db.commit()
    logger.info(f"Successfully processed order {order_id}")


def check_low_stock(db: Session) -> list:
    """
    Check for products with low stock levels.

    Args:
        db: Database session

    Returns:
        List of low stock items
    """
    low_stock_items = db.query(Inventory).filter(
        Inventory.quantity <= Inventory.reorder_level
    ).all()

    return low_stock_items
