# Best Practices: Structuring `src/app.py`

This guide demonstrates the recommended structure for a FastAPI application service within the x35 ecosystem. It synthesizes patterns from reference implementations and the `x35-fastapi` documentation to ensure consistency, testability, and robust resource management.

## Recommended Structure

The "Best Way" to create your `src/app.py` involves:

1.  **Early Logging Initialization**: Ensure logging is configured before other heavy imports if possible.
2.  **Explicit Imports**: Use the top-level package for `x35_fastapi` components.
3.  **Lifespan Management**: Use `asynccontextmanager` for resource setup and teardown.
4.  **Non-Blocking Startup and Runtime**: Ensure that any services with blocking I/O—both in their constructors and in their long-running methods (like a Kafka consumer loop)—are run in a separate thread to avoid stalling the server.
5.  **Factory Pattern**: Wrap app creation in a `create_app()` function to facilitate testing and configuration overrides.
6.  **Middleware**: Always include `CustomHeaderMiddleware` for distributed tracing.

---

### **Critical: Handling Blocking I/O in `lifespan`**

A common and severe pitfall is initializing or running a service that performs **blocking I/O**. This can happen in two places:

1.  **In the Constructor**: Calling a client like `MyKafkaConsumer()` might perform blocking network I/O during instantiation.
2.  **In the Runtime Loop**: A method like `consumer.consume_messages()` might block while polling for new messages, even if it's in an `async` function.

When this blocking code runs on the main asyncio event loop, it will **freeze the entire application**.

**Symptoms:**
*   **During Startup:** The Uvicorn server logs that it has started, but never prints the `Uvicorn running on http://...` message. The API is unreachable.
*   **During Runtime:** The server starts, but the first time the blocking code is called (e.g., the consumer starts its loop), all API endpoints will hang and become unresponsive.

**Solution:** All blocking operations must be delegated to a separate thread pool.
*   For blocking constructors, use `await asyncio.to_thread(create_blocking_clients)`.
*   For a long-running, blocking `async` function (like a consumer loop), run it in a separate thread using `loop.run_in_executor(None, lambda: asyncio.run(your_async_loop()))`.

---

## Annotated Example (with Non-Blocking Startup and Runtime)

```python
"""
Main application entry point.

This file configures the FastAPI application, initializes services,
and manages the application lifespan with a non-blocking background consumer.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from x35_fastapi import FastAPIAppBuilder, CustomHeaderMiddleware
from x35_json_logging import initialize_logging

from src.settings.app_settings import settings
from src.routes.health import version_router
from src.services.kafka_consumer import MyConsumerService 
from src.services.kafka_producer import MyProducerService

initialize_logging()
logger = logging.getLogger(f"x35.{__name__}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application lifecycle, ensuring a non-blocking startup and runtime.
    """
    
    def create_blocking_clients():
        """Synchronous function that instantiates clients with blocking constructors."""
        logger.info("Instantiating blocking clients in a dedicated thread...")
        producer = MyProducerService(topic=settings.producer_topic)
        consumer = MyConsumerService(topic=sesttings.consumer_topic)
        logger.info("Blocking clients instantiated.")
        return producer, consumer

    async def initialize_and_run_consumer():
        """
        Initializes services and starts the blocking consumer loop in a manner that
        does not stall the main FastAPI event loop.
        """
        try:
            # Step 1: Run blocking constructors in a thread.
            producer, consumer = await asyncio.to_thread(create_blocking_clients)
            app.state.producer = producer
            app.state.consumer = consumer
            
            # Step 2: Run the entire consumer's async run() method in a separate thread.
            # This is critical if the consumer's internal loop has blocking calls.
            logger.info("Starting consumer loop in background thread pool...")
            loop = asyncio.get_running_loop()
            app.state.consumer_task = loop.run_in_executor(
                None, lambda: asyncio.run(consumer.run())
            )
            logger.info("Consumer loop is running in the background.")

        except Exception as e:
            logger.critical(f"Failed to initialize background services: {e}", exc_info=True)

    # Launch the entire initialization and consumer startup as a background task.
    logger.info("Server starting, background services will initialize concurrently.")
    initialization_task = asyncio.create_task(initialize_and_run_consumer())

    yield

    # --- SHUTDOWN ---
    logger.info("Service shutting down...")
    
    if hasattr(app.state, "consumer_task") and app.state.consumer_task:
        # Since the task is in an executor, we can't asyncio.cancel it directly.
        # Proper shutdown would involve a custom signal handler in the consumer itself.
        # For simplicity, we acknowledge its presence. A real implementation
        # would need a more robust shutdown mechanism for thread executors.
        logger.info("Consumer task is running in a separate thread; initiating shutdown.")

    # Graceful Shutdown: Flush the producer
    if hasattr(app.state, "producer"):
        logger.info("Flushing Kafka producer...")
        try:
            await asyncio.to_thread(app.state.producer.flush)
            logger.info("Kafka producer flushed.")
        except Exception as e:
            logger.error(f"Error flushing producer: {e}")

    logger.info("Shutdown sequence completed.")


def create_app() -> FastAPI:
    """Application Factory."""
    builder = FastAPIAppBuilder(
        routers=[version_router],
        lifespan=lifespan,
        middleware=[CustomHeaderMiddleware] 
    )
    return builder.create_app()


# Global entry point
if __name__ == "__main__":
    logger.info("Starting FastAPI application via AppBuilder")
    builder = FastAPIAppBuilder(
        routers=[version_router],
        lifespan=lifespan,
        middleware=[CustomHeaderMiddleware]
    )
    builder.run()
```

## Key Components Checklist

| Component | Recommendation | Why? |
| :--- | :--- | :--- |
| **Blocking Constructors** | `await asyncio.to_thread(...)` | **Critical**: Prevents blocking constructors from freezing the event loop during startup. |
| **Blocking Runtimes** | `loop.run_in_executor(...)` | **Critical**: Runs long-running blocking processes (like a consumer loop) in a separate thread, keeping the API responsive. |
| **Middleware** | `CustomHeaderMiddleware` | Required for `X-Trace-ID` propagation in the x35 distributed system. |
| **Settings** | `src.settings` | Centralize config. Don't use `os.getenv` scattered in `app.py`. |
| **State** | `app.state.resource` | Store singletons (like producers) on `app.state` for easy access in dependencies. |
| **Shutdown** | `producer.flush()` | **Critical**: Prevents data loss by ensuring queued messages are sent before the process dies. |