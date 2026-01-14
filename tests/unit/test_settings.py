# -*- coding: utf-8 -*-
"""Unit tests for the settings module."""
import os
from unittest import mock

import pytest
from pydantic import ValidationError

from src.settings.config import get_settings


@pytest.fixture(autouse=True)
def _clear_env_vars():
    """Clear environment variables before each test."""
    with mock.patch.dict(os.environ, clear=True):
        get_settings.cache_clear()
        yield
        get_settings.cache_clear()


def test_app_settings_load_from_env(mocker):
    """Test that AppSettings loads settings from environment variables."""
    mocker.patch.dict(
        os.environ,
        {
            "BAMBOOROSE_API_URL": "https://test.com",
            "BAMBOOROSE_API_USERNAME": "test_user",
            "BAMBOOROSE_API_PASSWORD": "test_password",
            "BAMBOOROSE_API_TIMEOUT": "120",
            "X35_KAFKA_BOOTSTRAP_SERVERS": "kafka:9092",
            "X35_KAFKA_API_KEY": "kafka_key",
            "X35_KAFKA_API_SECRET": "kafka_secret",
            "X35_KAFKA_PRODUCER_TOPIC": "test-topic",
        },
    )
    settings = get_settings()
    assert settings.bamboorose.api_url == "https://test.com"
    assert settings.bamboorose.api_username == "test_user"
    assert settings.bamboorose.api_password.get_secret_value() == "test_password"
    assert settings.bamboorose.api_timeout == 120
    assert settings.kafka.bootstrap_servers == "kafka:9092"
    assert settings.kafka.api_key == "kafka_key"
    assert settings.kafka.api_secret == "kafka_secret"
    assert settings.kafka.producer_topic == "test-topic"


def test_app_settings_missing_required_env_vars():
    """Test that AppSettings raises ValidationError for missing required environment variables."""
    with pytest.raises(ValidationError):
        get_settings()


def test_app_settings_invalid_env_var_type(mocker):
    """Test that AppSettings raises ValidationError for invalid environment variable types."""
    mocker.patch.dict(
        os.environ,
        {
            "BAMBOOROSE_API_URL": "https://test.com",
            "BAMBOOROSE_API_USERNAME": "test_user",
            "BAMBOOROSE_API_PASSWORD": "test_password",
            "BAMBOOROSE_API_TIMEOUT": "not-an-integer",
            "X35_KAFKA_BOOTSTRAP_SERVERS": "kafka:9092",
            "X35_KAFKA_API_KEY": "kafka_key",
            "X35_KAFKA_API_SECRET": "kafka_secret",
        },
    )
    with pytest.raises(ValidationError):
        get_settings()


def test_app_settings_defaults(mocker):
    """Test that AppSettings uses default values when environment variables are not provided."""
    mocker.patch.dict(
        os.environ,
        {
            "BAMBOOROSE_API_URL": "https://test.com",
            "BAMBOOROSE_API_USERNAME": "test_user",
            "BAMBOOROSE_API_PASSWORD": "test_password",
            "X35_KAFKA_BOOTSTRAP_SERVERS": "kafka:9092",
            "X35_KAFKA_API_KEY": "kafka_key",
            "X35_KAFKA_API_SECRET": "kafka_secret",
        },
    )
    settings = get_settings()
    assert settings.bamboorose.api_timeout == 60
    assert settings.kafka.producer_topic == "x35-invoice-events"

