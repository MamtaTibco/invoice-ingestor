# -*- coding: utf-8 -*-
"""Application configuration."""
from functools import lru_cache
from typing import ClassVar

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from x35_settings.fastapi import FastAPISettings
from x35_settings.kafka import KafkaProducerSettings as X35KafkaProducerSettings


class BambooroseSettings(BaseSettings):
    """Bamboorose API settings."""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="BAMBOOROSE_",
        validate_assignment=True,
        extra="forbid",
    )

    api_url: str = Field(..., description="The URL of the Bamboorose API.")
    api_username: str = Field(..., description="The username for the Bamboorose API.")
    api_password: SecretStr = Field(..., description="The password for the Bamboorose API.")
    api_timeout: int = Field(60, description="The timeout in seconds for the Bamboorose API.")


class KafkaProducerSettings(X35KafkaProducerSettings):
    """Kafka producer settings."""

    producer_topic: str = Field(
        "x35-invoice-events", description="The Kafka topic to produce messages to."
    )


class AppSettings:
    """Application settings."""

    def __init__(self) -> None:
        """Initialize the application settings."""
        self.bamboorose = BambooroseSettings()
        self.kafka = KafkaProducerSettings()
        self.fastapi = FastAPISettings()


@lru_cache()
def get_settings() -> AppSettings:
    """Return the application settings."""
    return AppSettings()
