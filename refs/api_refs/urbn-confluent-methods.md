# `urbn-confluent-methods` API Reference

## Overview

The `urbn-confluent-methods` library provides high-level services for producing and consuming messages with Confluent Kafka. It simplifies interactions by handling configuration, serialization/deserialization with Schema Registry, and producer/consumer lifecycle management.

## Library Version

**Version:** `1.0.18`

## Configuration

The library is configured via environment variables, which are consumed by the underlying `urbn-confluent-config` package.

| Environment Variable | Description | Default |
| :--- | :--- | :--- |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka bootstrap servers. | (required) |
| `KAFKA_USERNAME` | Kafka username for SASL/PLAIN. | (required) |
| `KAFKA_PASSWORD` | Kafka password for SASL/PLAIN. | (required) |
| `SCHEMA_REGISTRY_URL` | Schema Registry URL. | (required) |
| `SCHEMA_REGISTRY_CREDENTIALS` | Schema Registry credentials (`user:password`). | (required) |
| `KAFKA_CONSUMER_GROUP` | Default Kafka consumer group. | (required for consumer) |
| `KAFKA_PRODUCER_ACKS` | Producer acknowledgment setting. | `all` |
| `KAFKA_AUTO_OFFSET_RESET` | Consumer auto offset reset policy. | `earliest` |
| `KAFKA_ENABLE_AUTO_COMMIT`| Enable auto commit for consumer. | `false` |
| `KAFKA_ENABLE_AUTO_OFFSET_STORE` | Enable auto offset store for consumer. | `false` |

## Core Concepts / How It Works

This library wraps the standard Confluent Kafka Python client to provide a more ergonomic API for common use cases:
- **Automatic Serialization**: seamlessly integrates with Schema Registry for JSON schema validation.
- **Lifecycle Management**: Simplifies producer/consumer setup and teardown.
- **Error Abstraction**: Provides unified `KafkaProducerError` and `KafkaConsumerError` exceptions.

## API Reference

### `ProducerService`

A service for producing messages to a specific Kafka topic.

**Constructor:** `ProducerService(topic: str, schema_id: Optional[int] = None)`

- **Parameters:**
  - `topic` (`str`): The Kafka topic to produce messages to.
  - `schema_id` (`Optional[int]`): The ID of the JSON schema in the Schema Registry to use for serialization. If `None`, messages are serialized as raw JSON strings.

#### `create_message`

Serializes and sends a single message to the configured topic.

- **Parameters:**
  - `message` (`Dict`): The message payload as a Python dictionary.
  - `key` (`Optional[str]`): The message key. If `None`, the current epoch time is used.
  - `log` (`bool`): Whether to log a confirmation message upon successful publishing. Defaults to `True`.

- **Returns:**
  - `None`

- **Exceptions:**
  - `KafkaProducerError`: If serialization or message delivery fails.

- **Example Usage:**
  ```python
  from urbn_confluent_methods import ProducerService, KafkaProducerError

  message = {
      "field1": "value1",
      "field2": 123
  }

  try:
      # Producer for a topic with schema validation
      producer = ProducerService(topic="my-structured-topic", schema_id=100001)
      producer.create_message(key="message-key-1", message=message)

      # Producer for a topic with raw JSON
      raw_producer = ProducerService(topic="my-raw-topic")
      raw_producer.create_message(key="message-key-2", message={"raw": "data"})

  except KafkaProducerError as e:
      print(f"Failed to send message: {e}")
  ```

### `ConsumerService`

A service for consuming messages from a specific Kafka topic.

**Constructor:** `ConsumerService(topic: str, schema_id: Optional[int] = None)`

- **Parameters:**
  - `topic` (`str`): The Kafka topic to consume from.
  - `schema_id` (`Optional[int]`): The ID of the JSON schema in the Schema Registry to use for deserialization. If `None`, the raw message value (bytes) is decoded as a UTF-8 string and parsed as JSON.

#### `consume_messages`

A generator that continuously polls for and yields messages from the topic. It handles deserialization automatically. The loop will terminate gracefully on `SIGTERM` or `SIGINT`.

- **Parameters:**
  - None

- **Yields:**
  - `dict`: A dictionary with keys `"key"` and `"value"`, where `"value"` is the deserialized message payload.

- **Exceptions:**
  - `KafkaConsumerError`: If polling or deserialization fails.

#### `handle_offset`

Manually stores and commits the offset for the last successfully processed message. This should be called after you have finished processing a message yielded by `consume_messages()`. This function respects the `KAFKA_ENABLE_AUTO_OFFSET_STORE` and `KAFKA_ENABLE_AUTO_COMMIT` settings.

- **Parameters:**
  - None

- **Returns:**
  - `None`

#### `seek_to_offset`

Resets the consumer's position to the offset of the last fetched message, allowing it to be re-processed. This is useful for implementing retry logic. It includes a random sleep interval to avoid tight retry loops.

- **Parameters:**
  - None

- **Returns:**
  - `None`

#### `stop_consumer`

Closes the consumer connection. This is called automatically when the `consume_messages` loop exits.

- **Parameters:**
  - None

- **Returns:**
  - `None`

- **Example Usage:**
  ```python
  from urbn_confluent_methods import ConsumerService, KafkaConsumerError

  try:
      # Consumer with schema validation
      consumer = ConsumerService(topic="my-structured-topic", schema_id=100001)

      print("Waiting for messages...")
      for message in consumer.consume_messages():
          print(f"Received key='{message['key']}', value={message['value']}")
          # Manually handle offset after processing
          consumer.handle_offset()

  except KafkaConsumerError as e:
      print(f"An error occurred: {e}")
  except KeyboardInterrupt:
      print("Consumer stopped.")
  ```

## Error Handling / Exceptions

### `KafkaProducerError`
Raised by `ProducerService` for any issues related to message production, including:
- Schema fetching failures.
- Message serialization errors.
- Message delivery failures reported by Kafka.

### `KafkaConsumerError`
Raised by `ConsumerService` for any issues related to message consumption, including:
- Schema fetching failures.
- Consumer connection or polling errors.

**Note:** Message deserialization errors are logged, and the message is skipped, but a `KafkaConsumerError` is not raised for individual message failures to prevent the consumer loop from crashing on bad data.