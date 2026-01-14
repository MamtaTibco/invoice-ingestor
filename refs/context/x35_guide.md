# X35 Guide

This guide offers a high-level overview of the x35 platform, outlining key concepts, tools, and recommended practices for developing and managing services.

## Introduction

The x35 Platform is a collection of cloud-native solutions and approaches built on GCP. It prioritizes scalability, security, and efficient data streaming. Infrastructure is managed using GitOps-driven CI/CD pipelines, ensuring consistent and reliable deployments across the platform.


## Core Libraries

Foundational x35 Python packages used across multiple services to ensure consistency and reliability. The core libraries are grouped by their primary function:


| Category | Library | Purpose | API Reference |
|----------|---------|---------|---------------|
| **Data Caching & Lookup** | `lookupcache` | Caches database lookup tables in memory to reduce database load and improve performance. | [API Reference](api_refs/lookupcache.md) |
| **Messaging & Streaming** | `urbn-confluent-methods` | Simplifies producing and consuming messages with Confluent Kafka. | [API Reference](api_refs/urbn-confluent-methods.md) |
| **Logging & Observability** | `x35-json-logging` | Produces structured JSON logs compatible with Google Cloud Logging. | [API Reference](api_refs/x35-json-logging.md) |
| **Configuration Management** | `x35-settings` | Manages application configuration via environment variables using Pydantic. | [API Reference](api_refs/x35-settings.md) |
| **Web Framework** | `x35-fastapi` | Provides a standardized builder for creating FastAPI applications. | [API Reference](api_refs/x35-fastapi.md) |
| **Error Handling** | `x35-errors` | Provides a set of standardized exception classes for consistent error handling across services. | [API Reference](api_refs/x35-errors.md) |

## External Libraries

Standard third-party Python libraries used alongside x35 core Libraries  for enhanced functionality.

| Category | Library | Purpose |
|----------|---------|---------|
| **XML Processing** | `xmltodict` | Converts XML documents to Python dictionaries and vice versa for easier data manipulation. |
| **XML Processing** | `lxml` | For XML Validation against XSD schemas|
| **Resilience & Retry** | `backoff` | Provides decorators for implementing exponential backoff and retry logic for transient failures. |

## Service Implementation Patterns

This section provides quick references to detailed implementation patterns and guidelines for building services on the x35 platform.

| Topic | Reference Path | Description |
|-------|---------------|-------------|
| **Message Processing Lifecycle** | [Reference](best_practices_and_patterns/service_patterns/message_processing_pattern.md#message-processing-lifecycle) | 8-step robust message processing flow: consume & extract context, validate with Pydantic, enrich from lookupcache, execute business logic, handle errors with retry (retryable vs non-retryable), publish to DLT, acknowledge offset, and handle system/other errors appropriately. |
| **Observability and Monitoring** | [Reference](best_practices_and_patterns/service_patterns/observability_and_monitoring_pattern.md#observability-and-monitoring) | Prometheus metrics implementation using `prometheus-client` library - includes Counter, Histogram, and Gauge metric examples for tracking messages, API latency, and resource usage. Exposes metrics via `/metrics` endpoint. Includes health check endpoint (`/health`) for deep dependency verification. |
| **Interacting with External Services** | [Reference](best_practices_and_patterns/service_patterns/interacting_with_external_services_pattern.md#interacting-with-external-services) | HTTP client patterns using `httpx` library for asynchronous requests with proper timeouts, connection limits, and retries. Includes client class design patterns with `x35-settings` integration for external API communication |
| **GCS File Handling Pattern** | [Reference](best_practices_and_patterns/gcs_file_handling_pattern.md#gcs-file-handling-pattern) | Complete file processing workflow with structured folder approach and comprehensive handling rules. Includes folder structure (`/input`, `/processed`, `/error`) and file handling rules (validation, locking, audit logging, retention policies). |
## Microservice project directory layout

```bash
src/                           # Source code
├── app.py                     # FastAPI application factory
├── models/                    # Data models and schemas
├── routes/                    # HTTP route handlers
├── services/                  # Business logic services
├── settings/                  # Configuration classes
└── utils/                     # Utility functions

tests/                         # Test suites
├── unit/                      # Unit tests
└── integration/               # Integration tests

scripts/                       # Development and testing scripts
```
