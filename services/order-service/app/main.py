"""Main application entry point for Order Service."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base
from .routes import router
from .pubsub import get_publisher

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
    logger.info("Starting Order Service...")
    logger.info(f"Environment: {settings.environment}")

    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")

    # Initialize Pub/Sub publisher
    publisher = get_publisher()
    logger.info(f"Pub/Sub publisher initialized (enabled: {publisher.enabled})")

    yield

    # Shutdown
    logger.info("Shutting down Order Service...")


# Create FastAPI application
app = FastAPI(
    title="Order Service",
    description="Microservice for managing customer orders",
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
        "service": "order-service",
        "environment": settings.environment,
        "pubsub_enabled": settings.enable_pubsub
    }


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Order Service",
        "version": "1.0.0",
        "description": "Manages customer orders and publishes events",
        "documentation": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.order_service_port,
        reload=settings.environment == "development"
    )
