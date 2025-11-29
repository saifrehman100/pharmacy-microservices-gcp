"""Configuration management for API Gateway."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Gateway
    api_gateway_port: int = 8000
    environment: str = "development"

    # JWT Configuration
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Service URLs (internal communication)
    product_service_url: str = "http://localhost:8001"
    order_service_url: str = "http://localhost:8002"
    inventory_service_url: str = "http://localhost:8003"

    # Rate Limiting
    rate_limit_per_minute: int = 60

    # Redis (for rate limiting and caching)
    redis_host: str = "localhost"
    redis_port: int = 6379

    # Database (for user authentication)
    database_url: str = "postgresql://postgres:postgres@localhost:5432/gateway_db"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
