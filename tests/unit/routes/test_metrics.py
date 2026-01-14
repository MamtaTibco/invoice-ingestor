# -*- coding: utf-8 -*-
"""Unit tests for the metrics endpoint."""
import pytest
from fastapi.testclient import TestClient

from src.app import create_app


@pytest.fixture
def test_client(mocker) -> TestClient:
    """Returns a test client with mocked settings."""
    mocker.patch("src.settings.config.BambooroseSettings")
    mocker.patch("src.settings.config.KafkaProducerSettings")
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_metrics(test_client: TestClient):
    """Test that the /metrics endpoint returns a 200 OK response and the Prometheus metrics."""
    response = test_client.get("/metrics")
    
    assert response.status_code == 200
    assert "invoices_fetched_total" in response.text
    assert "invoices_published_total" in response.text
    assert "bamboorose_api_requests_total" in response.text
    assert "bamboorose_api_request_duration_seconds" in response.text
    assert "kafka_produce_failures_total" in response.text
