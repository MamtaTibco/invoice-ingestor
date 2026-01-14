# `x35-errors` API Reference

## Overview

The `x35-errors` library provides a standardized framework for error handling across x35 microservices. It includes a catalog of predefined error codes and a hierarchy of custom exception classes. This promotes consistent error logging, reporting, and handling logic (e.g., retries).

## Library Version

**Version:** `0.1.4`

## Configuration

This library requires no configuration or environment variables.

## Core Concepts / How It Works

### `Error` Object
An `Error` object encapsulates the details of a specific error type. It is not meant to be instantiated directly but is used through the `ErrorCodes` catalog.
- `code` (`str`): A unique, standardized error code (e.g., `"ERR-1001"`).
- `message` (`str`): A default, human-readable description of the error.
- `http_status` (`int`): The suggested HTTP status code to return if this error surfaces through an API.

### `ErrorCodes` Catalog
A class that serves as a centralized catalog of predefined `Error` objects.

## API Reference

### `AppException`

The base exception class for all exceptions in this library.

**Constructor:**
```python
AppException(
    error: Error,
    message: Optional[str] = None,
    extra: Optional[dict] = None,
    cause: Optional[Exception] = None
)
```

- **Parameters:**
  - `error` (`Error`): The `Error` object from `ErrorCodes`.
  - `message` (`Optional[str]`): An optional message to override the default message from the `error` object.
  - `extra` (`Optional[dict]`): A dictionary of additional key-value pairs to include in structured logs.
  - `cause` (`Optional[Exception]`): The original exception that caused this one, for richer logging.

### `BlockingRetryException`

Used to signal that an operation failed but can be retried. The retry logic should block the current process (e.g., simple loop with sleep).

**Constructor:**
```python
BlockingRetryException(
    error: Error,
    message: Optional[str] = None,
    extra: Optional[dict] = None,
    cause: Optional[Exception] = None,
    retry_until_success: bool = False
)
```

- **Parameters:**
  - `retry_until_success` (`bool`): If `True`, the operation should be retried indefinitely. If `False` (default), it should be retried up to a configured maximum.
  - *(Inherits all parameters from `AppException`)*

### `NonBlockingRetryException`

Used to signal that an operation failed but can be retried. The retry should happen in the background, typically by sending the message to a retry topic.

**Constructor:**
```python
NonBlockingRetryException(
    error: Error,
    message: Optional[str] = None,
    extra: Optional[dict] = None,
    cause: Optional[Exception] = None,
    retry_until_success: bool = False,
    header: Optional[dict] = None
)
```

- **Parameters:**
  - `header` (`Optional[dict]`): A dictionary of headers to add to the message when sending to a retry topic.
  - *(Inherits all parameters from `BlockingRetryException`)*

### Other Exceptions

- `NonRetryableException`: Base for errors that should not be retried.
- `ValidationException`: For data validation failures.
- `TransformationException`: For data transformation failures.
- `DBException`: For database-related errors.
- `GcsException`: For Google Cloud Storage errors.
- `PrinterException`: For errors related to printing.
- `Kafka*Exception`: For various Kafka-related errors.

## Error Handling / Exceptions

This library is the foundation of error handling. Below are the common usage patterns.

### usage Patterns

**Raising an Exception:**
Always raise exceptions using an `Error` object from the `ErrorCodes` catalog.

```python
from x35_errors import ErrorCodes, ValidationException

def validate_data(data):
    if "required_field" not in data:
        raise ValidationException(
            error=ErrorCodes.ERR_1001,
            extra={"missing_field": "required_field"}
        )
```

**Wrapping an Original Exception:**
To preserve the stack trace of a caught exception, pass it as the `cause`.

```python
from x35_errors import ErrorCodes, GcsException
from google.cloud.exceptions import NotFound

try:
    # GCS client operation
    pass
except NotFound as e:
    raise GcsException(error=ErrorCodes.ERR_7005, cause=e)
```

**Logging Exceptions:**
When catching an `AppException`, its attributes can be used for structured logging.

```python
import logging
logger = logging.getLogger(__name__)

try:
    # operation
    pass
except AppException as e:
    logger.error(
        e.error_message,
        extra=e.extra,
        exc_info=True
    )
```

### Error Code Reference

| Range | Category |
| :--- | :--- |
| 1001-1200 | Validation Errors |
| 2001-2200 | Transformation Errors |
| 4001-4200 | Kafka Producer & Consumer Errors |
| 5001-5200 | API (REST/SOAP) Errors |
| 6001-6200 | Database Errors |
| 7001-7200 | Google Cloud Storage Errors |
| 8501-8600 | Printer Errors |
| 9001-9200 | Generic Application Errors |