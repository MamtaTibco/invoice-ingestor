# `x35-fastapi` API Reference

## Overview

The `x35-fastapi` library provides a standardized builder for creating FastAPI applications within the x35 ecosystem. It abstracts away boilerplate setup for servers, logging, and common endpoints, allowing developers to focus on business logic.

## Library Version

**Version:** `1.0.5`

## Configuration

This library is configured via environment variables through the `x35-settings` package.

- **`X35_FASTAPI_*`**: Controls FastAPI settings like enabling/disabling docs.
- **`X35_UVICORN_*`**: Controls Uvicorn server settings like port, workers, and log level.

## Core Concepts / How It Works

1.  **Standardization**: Provides a consistent way to initialize FastAPI apps with health checks, metrics, and version info.
2.  **Middleware Integration**: Automatically includes custom middleware for tracing (`X-Trace-ID`).
3.  **Lifespan Management**: Supports standard `asynccontextmanager` for app startup/shutdown logic.

### Built-in Endpoints
The `FastAPIAppBuilder` automatically includes the following endpoints:
- `GET /health`: Returns `{"status": "ok"}`.
- `GET /metrics`: Exposes application and system metrics in Prometheus format.
- `GET /version`: Returns build information from environment variables (`GIT_COMMIT`, `BUILD_TIMESTAMP`, `BUILD_LOG_URL`).

## API Reference

### `FastAPIAppBuilder`

The main class for constructing a FastAPI application.

**Constructor:**
```python
FastAPIAppBuilder(
    routers: Optional[List[APIRouter]] = None,
    lifespan: Optional[Callable] = None,
    middleware: Optional[List[BaseHTTPMiddleware]] = None
)
```

- **Parameters:**
  - `routers` (`Optional[List[APIRouter]]`): A list of FastAPI `APIRouter` objects that contain your application's endpoints.
  - `lifespan` (`Optional[Callable]`): An `asynccontextmanager` function to handle application startup and shutdown events.
  - `middleware` (`Optional[List[BaseHTTPMiddleware]]`): A list of custom Starlette/FastAPI middleware to be added to the application. `CustomHeaderMiddleware` is recommended.

#### `create_app`

Constructs the FastAPI application instance, including the provided routers, middleware, and built-in endpoints.

- **Returns:**
  - `FastAPI`: The configured FastAPI application instance.

#### `run`

Starts the Uvicorn server to run the application. This method should be called inside an `if __name__ == "__main__":` block.

- **Example Usage:**
  ```python
  from fastapi import APIRouter
  from x35_fastapi import FastAPIAppBuilder, CustomHeaderMiddleware
  from contextlib import asynccontextmanager

  # 1. Define routes
  my_router = APIRouter()
  @my_router.get("/my-endpoint")
  async def get_my_endpoint():
      return {"message": "Hello!"}

  # 2. Define lifespan
  @asynccontextmanager
  async def my_lifespan(app):
      print("Startup")
      yield
      print("Shutdown")

  # 3. Run
  if __name__ == "__main__":
      app_builder = FastAPIAppBuilder(
          routers=[my_router],
          lifespan=my_lifespan,
          middleware=[CustomHeaderMiddleware]
      )
      app_builder.run()
  ```

### `CustomHeaderMiddleware`

Middleware that handles the `X-Trace-ID` header for distributed tracing. It preserves existing headers or generates new UUIDs, adds the trace ID to logging context, and includes it in the response.

- **Usage:** Pass to `FastAPIAppBuilder`'s `middleware` list.

### `initialize_library_log_level`

A utility function to control the verbosity of common third-party libraries used in HTTP clients.

- **Parameters:**
  - `log_level` (`dict`): A dictionary mapping a `LogEnum` member to a Python logging level.

- **Example Usage:**
  ```python
  import logging
  from x35_fastapi import initialize_library_log_level, LogEnum

  # Suppress verbose httpx logs
  initialize_library_log_level({LogEnum.HTTPX: logging.WARNING})
  ```

## Error Handling / Exceptions

The library relies on FastAPI's standard exception handling. Uncaught exceptions are typically returned as 500 Internal Server Error responses.