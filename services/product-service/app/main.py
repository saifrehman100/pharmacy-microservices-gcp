"""Main application entry point for Product Service."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base
from .routes import router
from .models import Product  # Import models to register them with Base

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
    logger.info("Starting Product Service...")
    logger.info(f"Environment: {settings.environment}")

    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")

    yield

    # Shutdown
    logger.info("Shutting down Product Service...")


# Create FastAPI application
app = FastAPI(
    title="Product Service",
    description="Microservice for managing pharmacy products",
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
        "service": "product-service",
        "environment": settings.environment
    }


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Product Service",
        "version": "1.0.0",
        "description": "Manages pharmacy products and inventory items",
        "documentation": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.product_service_port,
        reload=settings.environment == "development"
    )
