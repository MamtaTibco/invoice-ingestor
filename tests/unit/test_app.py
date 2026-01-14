# -*- coding: utf-8 -*-
"""Unit tests for the main application logic."""
import asyncio
import logging
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI

# Mock the urbn_confluent_methods library to avoid the FileNotFoundError
sys.modules["urbn_confluent_methods"] = MagicMock()

from src.app import create_app, lifespan, process_invoices
from src.main import main


@pytest.mark.asyncio
async def test_process_invoices(mocker):
    """
    Test that the process_invoices function orchestrates the correct sequence of calls.
    
    This test mocks the functions that will be implemented in later steps and
    verifies that they are called in the correct order.
    """
    # These mocks will be replaced with actual implementations in later steps.
    logger_mock = mocker.patch("src.app.logger")
    trace_context_mock = mocker.patch("src.app.trace_context")
    bamboorose_client_mock = MagicMock()
    bamboorose_client_mock.get_invoices = AsyncMock(return_value=MagicMock(text="<xml/>"))
    mocker.patch("src.app.get_bamboorose_client", return_value=bamboorose_client_mock)
    
    kafka_producer_client_mock = MagicMock()
    mocker.patch("src.app.get_kafka_producer_client", return_value=kafka_producer_client_mock)
    
    parse_invoices_mock = mocker.patch("src.app.parse_invoices", return_value=["<invoice>1</invoice>", "<invoice>2</invoice>"])
    
    invoices_fetched_total_mock = mocker.patch("src.app.invoices_fetched_total")
    invoices_published_total_mock = mocker.patch("src.app.invoices_published_total")
    bamboorose_api_requests_total_mock = mocker.patch("src.app.bamboorose_api_requests_total")
    bamboorose_api_request_duration_seconds_mock = mocker.patch("src.app.bamboorose_api_request_duration_seconds")
    kafka_produce_failures_total_mock = mocker.patch("src.app.kafka_produce_failures_total")
    
    await process_invoices()
    
    trace_context_mock.assert_called_once()
    assert isinstance(trace_context_mock.call_args[0][0], str)
    
    bamboorose_client_mock.get_invoices.assert_awaited_once_with("2023-01-01T00:00:00Z")
    parse_invoices_mock.assert_called_once_with("<xml/>")
    
    assert kafka_producer_client_mock.publish_invoice.call_count == 2
    # The trace_id is a UUID, so we can't assert the exact value.
    # Instead, we will just assert that it is a string.
    assert isinstance(kafka_producer_client_mock.publish_invoice.call_args_list[0][0][1], str)
    
    invoices_fetched_total_mock.inc.assert_called_once_with(2)
    assert invoices_published_total_mock.inc.call_count == 2
    bamboorose_api_requests_total_mock.labels.assert_called_once_with(outcome="success")
    bamboorose_api_request_duration_seconds_mock.observe.assert_called_once()
    kafka_produce_failures_total_mock.inc.assert_not_called()
    
    assert mocker.call("Starting invoice processing run.") in logger_mock.info.call_args_list
    assert mocker.call(
        "Invoice processing run finished.",
        extra={"invoices_published": 2},
    ) in logger_mock.info.call_args_list


def test_create_app(mocker):
    """Test that the create_app function returns a FastAPI application."""
    mocker.patch(
        "src.app.get_settings",
        return_value=mocker.Mock(
            fastapi=mocker.Mock(enable_docs=True),
        ),
    )
    app = create_app()
    assert isinstance(app, FastAPI)


@pytest.mark.asyncio
async def test_lifespan(mocker):
    """Test that the lifespan context manager logs startup and shutdown messages."""
    logger_mock = mocker.patch("src.app.logger")
    get_kafka_producer_client_mock = mocker.patch("src.app.get_kafka_producer_client")
    app = FastAPI()
    
    async with lifespan(app):
        pass
    
    assert mocker.call("Application startup.") in logger_mock.info.call_args_list
    assert mocker.call("Application shutdown.") in logger_mock.info.call_args_list
    get_kafka_producer_client_mock.assert_called_once()


@pytest.mark.asyncio
async def test_main(mocker):
    """Test that the main function creates the app and calls process_invoices."""
    create_app_mock = mocker.patch("src.main.create_app")
    process_invoices_mock = mocker.patch("src.main.process_invoices", new_callable=AsyncMock)
    
    await main()
    
    create_app_mock.assert_called_once()
    process_invoices_mock.assert_awaited_once()
