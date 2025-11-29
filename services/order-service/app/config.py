"""Configuration management for Order Service."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Service Configuration
    order_service_port: int = 8002
    environment: str = "development"

    # Database Configuration
    database_url: str = "postgresql://postgres:postgres@localhost:5432/order_db"

    # GCP Pub/Sub Configuration
    gcp_project_id: str = "your-gcp-project-id"
    pubsub_order_topic: str = "order-events"
    google_application_credentials: Optional[str] = None

    # Enable/Disable Pub/Sub (for local development without GCP)
    enable_pubsub: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
