# -*- coding: utf-8 -*-
"""Prometheus metrics."""
from prometheus_client import Counter, Histogram

invoices_fetched_total = Counter(
    "invoices_fetched_total",
    "The total number of individual invoices fetched from the Bamboorose API.",
)

invoices_published_total = Counter(
    "invoices_published_total",
    "The total number of invoices successfully published to Kafka.",
)

bamboorose_api_requests_total = Counter(
    "bamboorose_api_requests_total",
    "The total number of requests made to the Bamboorose API.",
    ["outcome"],
)

bamboorose_api_request_duration_seconds = Histogram(
    "bamboorose_api_request_duration_seconds",
    "The latency of requests to the Bamboorose API.",
)

kafka_produce_failures_total = Counter(
    "kafka_produce_failures_total",
    "A counter that increments each time a message fails to be produced to Kafka after all internal retries.",
)
