"""Google Cloud Pub/Sub subscriber for order events."""
import json
import logging
import asyncio
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
from google.cloud import pubsub_v1
from google.api_core import exceptions as gcp_exceptions

from .config import settings
from .database import SessionLocal
from .inventory_service import process_order_event

logger = logging.getLogger(__name__)


class PubSubSubscriber:
    """
    Wrapper for Google Cloud Pub/Sub subscriber.

    This class listens to order events and processes them to update inventory.
    If Pub/Sub is disabled, it won't start the subscriber.
    """

    def __init__(self):
        self.enabled = settings.enable_pubsub
        self.project_id = settings.gcp_project_id
        self.subscription_name = settings.pubsub_order_subscription
        self.subscriber = None
        self.subscription_path = None
        self.streaming_pull_future = None
        self.executor = ThreadPoolExecutor(max_workers=10)

        if self.enabled:
            try:
                self.subscriber = pubsub_v1.SubscriberClient()
                self.subscription_path = self.subscriber.subscription_path(
                    self.project_id,
                    self.subscription_name
                )
                logger.info(f"Pub/Sub subscriber initialized for: {self.subscription_path}")
            except Exception as e:
                logger.warning(
                    f"Failed to initialize Pub/Sub subscriber: {e}. "
                    "Subscriber will not run."
                )
                self.enabled = False
        else:
            logger.info("Pub/Sub is disabled. Subscriber will not run.")

    def message_callback(self, message):
        """
        Callback for processing received Pub/Sub messages.

        Args:
            message: Pub/Sub message object
        """
        try:
            # Parse message data
            data = json.loads(message.data.decode("utf-8"))
            event_type = data.get("event_type")

            logger.info(f"Received Pub/Sub message: {event_type}")

            # Process order.created events
            if event_type == "order.created":
                db = SessionLocal()
                try:
                    process_order_event(db, data)
                    message.ack()
                    logger.info(f"Processed order event: {data.get('order_id')}")
                except Exception as e:
                    logger.error(f"Error processing order event: {e}")
                    message.nack()
                finally:
                    db.close()
            else:
                # Acknowledge other event types (not processed by inventory)
                message.ack()

        except Exception as e:
            logger.error(f"Error in message callback: {e}")
            message.nack()

    def start(self):
        """Start the Pub/Sub subscriber."""
        if not self.enabled or not self.subscriber:
            logger.info("Pub/Sub subscriber not started (disabled or not initialized)")
            return

        try:
            logger.info(f"Starting Pub/Sub subscriber for: {self.subscription_path}")

            # Subscribe with callback
            self.streaming_pull_future = self.subscriber.subscribe(
                self.subscription_path,
                callback=self.message_callback
            )

            logger.info("Pub/Sub subscriber started successfully")

            # Keep the subscriber running in background
            # Note: In production, you might want to handle this differently
            # or run it in a separate container/process

        except gcp_exceptions.GoogleAPIError as e:
            logger.error(f"Failed to start Pub/Sub subscriber: {e}")
            self.enabled = False
        except Exception as e:
            logger.error(f"Unexpected error starting subscriber: {e}")
            self.enabled = False

    def stop(self):
        """Stop the Pub/Sub subscriber."""
        if self.streaming_pull_future:
            logger.info("Stopping Pub/Sub subscriber...")
            self.streaming_pull_future.cancel()
            try:
                self.streaming_pull_future.result(timeout=10)
            except Exception:
                pass
            logger.info("Pub/Sub subscriber stopped")

        if self.executor:
            self.executor.shutdown(wait=True)


# Global subscriber instance
_subscriber: Optional[PubSubSubscriber] = None


def get_subscriber() -> PubSubSubscriber:
    """Get or create the global subscriber instance."""
    global _subscriber
    if _subscriber is None:
        _subscriber = PubSubSubscriber()
    return _subscriber
