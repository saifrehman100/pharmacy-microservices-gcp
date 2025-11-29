"""Google Cloud Pub/Sub integration for publishing order events."""
import json
import logging
from typing import Dict, Any, Optional
from google.cloud import pubsub_v1
from google.api_core import exceptions as gcp_exceptions

from .config import settings

logger = logging.getLogger(__name__)


class PubSubPublisher:
    """Wrapper for Google Cloud Pub/Sub publisher.

    This class handles publishing order events to GCP Pub/Sub.
    If Pub/Sub is disabled (for local development), it logs the events instead.
    """

    def __init__(self):
        self.enabled = settings.enable_pubsub
        self.project_id = settings.gcp_project_id
        self.topic_name = settings.pubsub_order_topic
        self.publisher = None
        self.topic_path = None

        if self.enabled:
            try:
                self.publisher = pubsub_v1.PublisherClient()
                self.topic_path = self.publisher.topic_path(
                    self.project_id,
                    self.topic_name
                )
                logger.info(f"Pub/Sub publisher initialized for topic: {self.topic_path}")
            except Exception as e:
                logger.warning(
                    f"Failed to initialize Pub/Sub publisher: {e}. "
                    "Events will be logged instead."
                )
                self.enabled = False
        else:
            logger.info("Pub/Sub is disabled. Events will be logged only.")

    async def publish_order_created(self, order_data: Dict[str, Any]) -> Optional[str]:
        """
        Publish order created event to Pub/Sub.

        Args:
            order_data: Dictionary containing order information

        Returns:
            Message ID if published successfully, None otherwise
        """
        event = {
            "event_type": "order.created",
            "order_id": order_data.get("id"),
            "user_id": order_data.get("user_id"),
            "products": order_data.get("products"),
            "total_amount": order_data.get("total_amount"),
            "timestamp": order_data.get("created_at").isoformat() if order_data.get("created_at") else None
        }

        return await self._publish_event(event)

    async def publish_order_status_changed(
        self,
        order_id: int,
        old_status: str,
        new_status: str
    ) -> Optional[str]:
        """
        Publish order status change event to Pub/Sub.

        Args:
            order_id: Order ID
            old_status: Previous status
            new_status: New status

        Returns:
            Message ID if published successfully, None otherwise
        """
        event = {
            "event_type": "order.status_changed",
            "order_id": order_id,
            "old_status": old_status,
            "new_status": new_status
        }

        return await self._publish_event(event)

    async def _publish_event(self, event: Dict[str, Any]) -> Optional[str]:
        """
        Internal method to publish event to Pub/Sub or log it.

        Args:
            event: Event data to publish

        Returns:
            Message ID if published successfully, None otherwise
        """
        if not self.enabled or not self.publisher:
            # Log event if Pub/Sub is disabled
            logger.info(f"[Pub/Sub Disabled] Event: {json.dumps(event, default=str)}")
            return None

        try:
            # Convert event to JSON bytes
            data = json.dumps(event, default=str).encode("utf-8")

            # Publish to Pub/Sub
            future = self.publisher.publish(self.topic_path, data)
            message_id = future.result(timeout=5.0)

            logger.info(f"Published event to Pub/Sub: {event['event_type']} (message_id: {message_id})")
            return message_id

        except gcp_exceptions.GoogleAPIError as e:
            logger.error(f"Failed to publish event to Pub/Sub: {e}")
            logger.info(f"Event that failed to publish: {json.dumps(event, default=str)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error publishing event: {e}")
            return None


# Global publisher instance
_publisher: Optional[PubSubPublisher] = None


def get_publisher() -> PubSubPublisher:
    """Get or create the global publisher instance."""
    global _publisher
    if _publisher is None:
        _publisher = PubSubPublisher()
    return _publisher
