# -*- coding: utf-8 -*-
"""Unit tests for the Kafka client."""
import sys
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

# Mock the urbn_confluent_methods library to avoid the FileNotFoundError
class KafkaProducerError(Exception):
    pass

urbn_confluent_methods = MagicMock()
urbn_confluent_methods.KafkaProducerError = KafkaProducerError
sys.modules["urbn_confluent_methods"] = urbn_confluent_methods

from src.clients.kafka import KafkaProducerClient, get_kafka_producer_client


@pytest.fixture
def kafka_producer_client(mocker: MockerFixture) -> KafkaProducerClient:
    """Returns a Kafka producer client with a mocked ProducerService."""
    mocker.patch(
        "src.clients.kafka.get_settings",
        return_value=mocker.Mock(
            kafka=mocker.Mock(
                producer_topic="test-topic",
            ),
        ),
    )
    return get_kafka_producer_client()


def test_publish_invoice(kafka_producer_client: KafkaProducerClient, mocker: MockerFixture):
    """Test that the publish_invoice method calls the create_message method with the correct arguments."""
    kafka_producer_client.publish_invoice("<invoice>test</invoice>", "test-trace-id")
    
    kafka_producer_client.producer.create_message.assert_called_once_with(
        key="test-trace-id",
        message={"invoice": "<invoice>test</invoice>"},
        headers={"trace_id": "test-trace-id"},
    )


def test_publish_invoice_error(kafka_producer_client: KafkaProducerClient, mocker: MockerFixture):
    """Test that the publish_invoice method raises a KafkaProducerError when the producer fails."""
    kafka_producer_client.producer.create_message.side_effect = KafkaProducerError
    
    with pytest.raises(KafkaProducerError):
        kafka_producer_client.publish_invoice("<invoice>test</invoice>", "test-trace-id")
