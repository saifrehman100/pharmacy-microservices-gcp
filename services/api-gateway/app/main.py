"""Main application entry point for API Gateway."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base
from .middleware import LoggingMiddleware, RateLimitMiddleware
from .routes import auth_router, proxy_router
from .models import User  # Import models to register them with Base

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
    logger.info("Starting API Gateway...")
    logger.info(f"Environment: {settings.environment}")

    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")

    yield

    # Shutdown
    logger.info("Shutting down API Gateway...")


# Create FastAPI application
app = FastAPI(
    title="Pharmacy Microservices - API Gateway",
    description="API Gateway for Pharmacy Order Management System",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    max_requests=settings.rate_limit_per_minute,
    window_seconds=60
)

# Include routers
app.include_router(auth_router)
app.include_router(proxy_router)


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "environment": settings.environment
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Pharmacy Microservices API Gateway",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.api_gateway_port,
        reload=settings.environment == "development"
    )
