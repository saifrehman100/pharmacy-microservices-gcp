"""API routes for authentication and proxying."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta

from .database import get_db
from .models import User
from .schemas import UserCreate, UserResponse, Token, LoginRequest
from .auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user
)
from .config import settings
from .proxy import forward_request

# Create routers
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
proxy_router = APIRouter(tags=["Proxy"])


@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@auth_router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    user = authenticate_user(db, login_data.username, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


# Product Service Proxy Routes
@proxy_router.get("/products")
async def get_products(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Proxy to Product Service - List all products."""
    return await forward_request(request, settings.product_service_url, "products")


@proxy_router.get("/products/{product_id}")
async def get_product(
    request: Request,
    product_id: int,
    current_user: User = Depends(get_current_user)
):
    """Proxy to Product Service - Get specific product."""
    return await forward_request(
        request,
        settings.product_service_url,
        f"products/{product_id}"
    )


@proxy_router.post("/products")
async def create_product(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Proxy to Product Service - Create new product."""
    return await forward_request(request, settings.product_service_url, "products")


@proxy_router.put("/products/{product_id}")
async def update_product(
    request: Request,
    product_id: int,
    current_user: User = Depends(get_current_user)
):
    """Proxy to Product Service - Update product."""
    return await forward_request(
        request,
        settings.product_service_url,
        f"products/{product_id}"
    )


@proxy_router.delete("/products/{product_id}")
async def delete_product(
    request: Request,
    product_id: int,
    current_user: User = Depends(get_current_user)
):
    """Proxy to Product Service - Delete product."""
    return await forward_request(
        request,
        settings.product_service_url,
        f"products/{product_id}"
    )


@proxy_router.get("/products/search")
async def search_products(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Proxy to Product Service - Search products."""
    return await forward_request(request, settings.product_service_url, "products/search")


# Order Service Proxy Routes
@proxy_router.post("/orders")
async def create_order(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Proxy to Order Service - Create new order."""
    return await forward_request(request, settings.order_service_url, "orders")


@proxy_router.get("/orders/{order_id}")
async def get_order(
    request: Request,
    order_id: int,
    current_user: User = Depends(get_current_user)
):
    """Proxy to Order Service - Get specific order."""
    return await forward_request(
        request,
        settings.order_service_url,
        f"orders/{order_id}"
    )


@proxy_router.get("/orders/user/{user_id}")
async def get_user_orders(
    request: Request,
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Proxy to Order Service - Get user's orders."""
    return await forward_request(
        request,
        settings.order_service_url,
        f"orders/user/{user_id}"
    )


@proxy_router.put("/orders/{order_id}/status")
async def update_order_status(
    request: Request,
    order_id: int,
    current_user: User = Depends(get_current_user)
):
    """Proxy to Order Service - Update order status."""
    return await forward_request(
        request,
        settings.order_service_url,
        f"orders/{order_id}/status"
    )


# Inventory Service Proxy Routes
@proxy_router.get("/inventory/{product_id}")
async def get_inventory(
    request: Request,
    product_id: int,
    current_user: User = Depends(get_current_user)
):
    """Proxy to Inventory Service - Get product inventory."""
    return await forward_request(
        request,
        settings.inventory_service_url,
        f"inventory/{product_id}"
    )


@proxy_router.put("/inventory/{product_id}/adjust")
async def adjust_inventory(
    request: Request,
    product_id: int,
    current_user: User = Depends(get_current_user)
):
    """Proxy to Inventory Service - Adjust inventory."""
    return await forward_request(
        request,
        settings.inventory_service_url,
        f"inventory/{product_id}/adjust"
    )


@proxy_router.get("/inventory/low-stock")
async def get_low_stock(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Proxy to Inventory Service - Get low stock items."""
    return await forward_request(
        request,
        settings.inventory_service_url,
        "inventory/low-stock"
    )
