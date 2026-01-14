# `x35-json-logging` API Reference

## Overview

The `x35-json-logging` library provides structured JSON logging capabilities for x35 microservices. It ensures consistent log formats, handles context propagation (like trace IDs), and integrates seamlessly with the Python standard logging module.

## Library Version

**Version:** `0.1.6`

## Configuration

The library is configured via environment variables, which are loaded by the `LoggingSettings` class.

| Environment Variable | Description | Default Value |
| :--- | :--- | :--- |
| `X35_LOGGING_LOG_LEVEL` | Sets the logging level for the application. | `INFO` |
| `X35_LOGGING_SERVICE_NAME` | Specifies the name of the service, which will be included in all log records. | `***` |

## Core Concepts / How It Works

- **Structured Output**: Uses a custom `JsonFormatter` (`X35JsonLogging`) to output logs as JSON objects.
- **Context Propagation**: Uses `contextvars` to maintain context (like trace IDs) across asynchronous calls.
- **Enums**: Provides `LogFieldEnum` and `HeaderEnum` to standardize field names.

## API Reference

### Core Functions

#### `initialize_logging`

Configures the Python logging system to use the custom `X35JsonLogging` formatter. It should be called once at application startup.

- **Parameters:**
  - `additional_settings` (`dict | None`): A dictionary of logging settings to merge with the default configuration.

- **Example Usage:**
  ```python
  import logging
  from x35_json_logging import initialize_logging

  # Basic initialization
  initialize_logging()

  # With custom settings
  initialize_logging(additional_settings={"root": {"level": "DEBUG"}})
  ```

### Context Managers

#### `trace_context`

A context manager to set a `trace_id` for all logs generated within its scope. The trace ID is automatically cleared upon exiting the context.

- **Parameters:**
  - `trace_id` (`str`): The identifier for the current trace or request.

- **Example Usage:**
  ```python
  from x35_json_logging import trace_context
  import logging
  logger = logging.getLogger("x35")

  with trace_context("req-123"):
      logger.info("Log with trace_id")
  ```

#### `dynamic_context`

A flexible context manager to set any number of custom context variables for logging.

- **Parameters:**
  - `**kwargs`: Keyword arguments where the key is the desired field name and the value is the string value.

- **Example Usage:**
  ```python
  from x35_json_logging import dynamic_context, LogFieldEnum
  
  with dynamic_context(span_id="span-1", **{LogFieldEnum.REQUEST_ID: "req-1"}):
      logger.info("Log with multiple context fields")
  ```

### Enums

#### `LogFieldEnum`
Standard field names for structured logs.
- `TRACE_ID` (`"trace_id"`)
- `REQUEST_ID` (`"request_id"`)
- `SPAN_ID` (`"span_id"`)
- `SEQUENCE_NUMBER` (`"sequence_number"`)
- `ERROR_CODE` (`"error_code"`)
- `ERROR_MESSAGE` (`"error_message"`)
- `CAUSE` (`"cause"`)
- `AUDIT_ATTACHMENTS_DATA` (`"audit.attachments.data"`)

#### `HeaderEnum`
Standard header names for HTTP requests or Kafka messages.
- `X_TRACE_ID` (`"X-Trace-ID"`)
- `TRACE_ID` (`"trace_id"`)
- `REQUEST_ID` (`"request_id"`)
- `SPAN_ID` (`"span_id"`)
- `SEQUENCE_NUMBER` (`"sequence_number"`)

### Low-Level Components

#### `trace_id_var`
The underlying `contextvars.ContextVar` instance for the trace ID. Can be used for manual context management.

- **Example Usage:**
  ```python
  from x35_json_logging import trace_id_var
  token = trace_id_var.set("id")
  # ...
  trace_id_var.reset(token)
  ```

## Error Handling / Exceptions

This library is designed to be robust and generally does not raise exceptions during normal logging operations. Misconfiguration of the `initialize_logging` dictionary may raise `ValueError` or `KeyError` from the standard `logging.config` module.