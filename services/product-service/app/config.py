"""Configuration management for Product Service."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Service Configuration
    product_service_port: int = 8001
    environment: str = "development"

    # Database Configuration
    database_url: str = "postgresql://postgres:postgres@localhost:5432/product_db"

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
