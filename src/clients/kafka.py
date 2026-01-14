# -*- coding: utf-8 -*-
"""Client for interacting with Kafka."""
import asyncio
import logging

from urbn_confluent_methods import ProducerService, KafkaProducerError
from x35_json_logging import dynamic_context

from src.settings.config import get_settings

logger = logging.getLogger(f"x35.{__name__}")


class KafkaProducerClient:
    """A client for producing messages to Kafka."""

    def __init__(self) -> None:
        """Initializes the Kafka producer client."""
        settings = get_settings()
        self.producer = ProducerService(topic=settings.kafka.producer_topic)

    async def publish_invoice(self, invoice: str, trace_id: str) -> None:
        """
        Publishes an invoice to Kafka asynchronously.

        Args:
            invoice: The invoice to publish.
            trace_id: The trace ID for the request.
        """
        try:
            await asyncio.to_thread(
                self.producer.create_message,
                key=trace_id,
                message={"invoice": invoice},
                headers={"trace_id": trace_id},
            )
        except KafkaProducerError as e:
            with dynamic_context(trace_id=trace_id):
                logger.error("Failed to publish message to Kafka", exc_info=e)
            raise


def get_kafka_producer_client() -> KafkaProducerClient:
    """
    Returns an instance of the Kafka producer client.

    This function is used to inject the client into the application.
    """
    return KafkaProducerClient()
