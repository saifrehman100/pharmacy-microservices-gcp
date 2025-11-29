"""Configuration management for Inventory Service."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Service Configuration
    inventory_service_port: int = 8003
    environment: str = "development"

    # Database Configuration
    database_url: str = "postgresql://postgres:postgres@localhost:5432/inventory_db"

    # GCP Pub/Sub Configuration
    gcp_project_id: str = "your-gcp-project-id"
    pubsub_order_topic: str = "order-events"
    pubsub_order_subscription: str = "inventory-order-subscription"
    google_application_credentials: Optional[str] = None

    # Enable/Disable Pub/Sub (for local development without GCP)
    enable_pubsub: bool = True

    # Inventory Alerts
    low_stock_threshold: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
