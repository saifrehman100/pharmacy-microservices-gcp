"""Main application entry point for Inventory Service."""
import logging
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base
from .routes import router
from .pubsub_subscriber import get_subscriber
from .models import Inventory  # Import models to register them with Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Inventory Service...")
    logger.info(f"Environment: {settings.environment}")

    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")

    # Start Pub/Sub subscriber in background thread
    subscriber = get_subscriber()
    if subscriber.enabled:
        subscriber_thread = threading.Thread(target=subscriber.start, daemon=True)
        subscriber_thread.start()
        logger.info("Pub/Sub subscriber thread started")
    else:
        logger.info("Pub/Sub subscriber not started (disabled)")

    yield

    # Shutdown
    logger.info("Shutting down Inventory Service...")
    if subscriber.enabled:
        subscriber.stop()


# Create FastAPI application
app = FastAPI(
    title="Inventory Service",
    description="Microservice for managing product inventory levels",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return {
        "status": "healthy",
        "service": "inventory-service",
        "environment": settings.environment,
        "pubsub_enabled": settings.enable_pubsub
    }


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Inventory Service",
        "version": "1.0.0",
        "description": "Manages product inventory and processes order events",
        "documentation": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.inventory_service_port,
        reload=settings.environment == "development"
    )
