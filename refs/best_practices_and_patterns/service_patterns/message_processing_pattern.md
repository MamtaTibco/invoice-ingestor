
### Message Processing Lifecycle

A robust message processing flow is critical for consumer-based services. This pattern provides a reliable blueprint.

1.  **Consume and Extract Context**: A message is consumed from Kafka. A `trace_id` is extracted from the message headers for distributed tracing.
2.  **Validate**: The message payload is validated against a Pydantic model. If validation fails, it's a non-retryable error; the message is logged as an error and acknowledged (skipped) to prevent blocking the consumer.
3.  **Enrich**: The data is enriched with information from the `lookupcache`. If enrichment fails (e.g., a key is not found), it is treated as a non-retryable error (logged and acknowledged).
4.  **Execute Business Logic**: The core business logic is executed (e.g., calling an external API).
5.  **Handle Errors with Retry**:
    - **Retryable Errors**: For transient failures (e.g., network errors, `5xx` HTTP status codes), a `RetryableException` is raised. The consumer should catch this and re-process the message up to a defined `MAX_RETRIES` limit.
    - **Non-Retryable Errors**: For permanent failures (e.g., validation errors, `4xx` HTTP status codes), a `NonRetryableException` is raised. The consumer should not retry these messages.
6.  **Publish to DLT**: If a message fails after all retry attempts (Retryable Errors), or if an unexpected system error occurs, it is published to a Dead Letter Topic (DLT) for later analysis. Non-retryable business/validation errors are typically logged and dropped (not sent to DLT) to avoid cluttering the DLT with invalid data.
7.  **Acknowledge**: The message offset is committed only after the message has been successfully processed or definitively handled (e.g., sent to the DLT or acknowledged after a non-retryable error).
8.  **Handling Errors**:
    - **System Errors:** If Kafka/Network/System issues persist after retries, these messages are pushed to DLT.
    - **Data/Business Errors:** Do not push these to DLT. Log them clearly (e.g., using `x35-json-logging`) and acknowledge the message.
