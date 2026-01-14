
### Observability and Monitoring

In addition to the structured logging provided by `x35-json-logging`, services should expose metrics for monitoring and alerting.

-   **Metrics**: Use the `prometheus-client` library to create and expose metrics via a `/metrics` endpoint. Key metrics to track include:
    -   `Counter`: For tracking events like messages consumed, messages processed successfully, and messages sent to the DLT.
    -   `Histogram`: For measuring the duration of operations like external API calls.
    -   `Gauge`: For tracking values that can go up and down, like memory or CPU usage.
```python
    # Example of Prometheus metrics
    from prometheus_client import Counter, Histogram

    MESSAGES_CONSUMED = Counter(
        "messages_consumed_total",
        "Total number of messages consumed from Kafka",
    )

    EXTERNAL_API_DURATION = Histogram(
        "external_api_duration_seconds",
        "Latency of external API calls in seconds",
        ["action"],
    )
```

-   **Health Checks**: A `/health` endpoint is essential for service monitoring. This endpoint should perform "deep" health checks, verifying the status of all critical dependencies.

    -   **Implementation**: The health check should return a `200 OK` status if all dependencies are healthy. If any dependency is unhealthy, it should return a `503 Service Unavailable` status with a descriptive error message.
```python
    # Example of a health check endpoint
    async def health_check(response: Response) -> HealthResponse:
        db_status = await lookup_cache.is_connected()
        kafka_status = consumer.is_connected()

        if not db_status or not kafka_status:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            # ... return details

        return HealthResponse(status="UP")
```
