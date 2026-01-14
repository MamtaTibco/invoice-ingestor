# `x35-settings` API Reference

## Overview

The `x35-settings` library provides a standardized, `pydantic`-based solution for managing application configuration via environment variables. It offers pre-defined settings classes for common components used across the x35 platform, such as FastAPI, Uvicorn, Kafka, and logging.

## Library Version

**Version:** `1.1.0`

## Configuration

This library is the configuration mechanism itself. It relies on `pydantic-settings` to load values from environment variables or `.env` files.

## Core Concepts / How It Works

- **BaseSettings**: The foundation class that handles environment variable loading.
- **Component Classes**: Specialized classes (`FastAPISettings`, `UvicornSettings`, etc.) pre-configured with standard defaults and prefixes.
- **Composition**: Encourages creating a single `AppSettings` class that composes these smaller settings classes.

## API Reference

### Settings Classes

#### `BaseSettings`
The foundation for all other settings classes. Provides functionality for loading from `.env` files.

#### `FastAPISettings`
Configures the FastAPI application.
- **Prefix:** `X35_FASTAPI_`
- **Fields:**
  - `enable_docs` (`bool`): Default `False`.
  - `root_path` (`str`): Default `""`.

#### `UvicornSettings`
Configures the Uvicorn ASGI server.
- **Prefix:** `X35_UVICORN_`
- **Fields:**
  - `port` (`int`): Default `8080`.
  - `workers` (`int`): Default `1`.
  - `log_level` (`str`): Default `"info"`.
  - `reload` (`bool`): Default `False`.
  - `access_log` (`bool`): Default `True`.

#### `LoggingSettings`
Configures the `x35-json-logging` library.
- **Prefix:** `X35_LOGGING_`
- **Fields:**
  - `log_level` (`str`): Default `"INFO"`.
  - `service_name` (`str`): Default `"***"`.

#### `KafkaConsumerSettings`
Configures Kafka consumers.
- **Prefix:** `X35_KAFKA_`
- **Fields:**
  - `bootstrap_servers` (`str`): **Required**.
  - `api_key` (`str`): **Required**.
  - `api_secret` (`str`): **Required**.
  - `group_id` (`str`): **Required**.
  - `auto_offset_reset` (`str`): Default `"earliest"`.
  - `enable_auto_commit` (`bool`): Default `False`.

#### `KafkaProducerSettings`
Configures Kafka producers.
- **Prefix:** `X35_KAFKA_`
- **Fields:**
  - `bootstrap_servers` (`str`): **Required**.
  - `api_key` (`str`): **Required**.
  - `api_secret` (`str`): **Required**.
  - `acks` (`str`): Default `"all"`.
  - `enable_idempotence` (`bool`): Default `True`.
  - `retries` (`int`): Default `5`.

### Usage Patterns

#### Basic Instantiation
```python
from x35_settings import UvicornSettings
settings = UvicornSettings() # Loads X35_UVICORN_*
```

#### Unified Settings Class
```python
from x35_settings import FastAPISettings, UvicornSettings

class AppSettings:
    def __init__(self):
        self.fastapi = FastAPISettings()
        self.uvicorn = UvicornSettings()

settings = AppSettings()
```

#### Custom Application Settings
Extend `BaseSettings` to define your own configuration.

```python
from typing import ClassVar
from x35_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from pydantic import Field

class DatabaseSettings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="DATABASE_",
        validate_assignment=True,
        extra="forbid",
    )
    host: str = Field(..., description="DB Host")
    
# Loads DATABASE_HOST
db_settings = DatabaseSettings()
```

## Error Handling / Exceptions

`pydantic.ValidationError` is raised if required environment variables are missing or if values do not match the expected types (e.g., passing a string to an `int` field). This usually happens at application startup, ensuring fail-fast behavior.