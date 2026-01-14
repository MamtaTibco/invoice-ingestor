# -*- coding: utf-8 -*-
"""Unit tests for the Bamboorose client."""
import httpx
import pytest
import respx

from src.clients.bamboorose import BambooroseClient, get_bamboorose_client


@pytest.fixture
def bamboorose_client(mocker) -> BambooroseClient:
    """Returns a Bamboorose client with mocked settings."""
    mocker.patch(
        "src.clients.bamboorose.get_settings",
        return_value=mocker.Mock(
            bamboorose=mocker.Mock(
                api_url="https://test.com",
                api_timeout=60,
                api_username="test_user",
                api_password=mocker.Mock(get_secret_value=lambda: "test_password"),
            ),
        ),
    )
    return get_bamboorose_client()


@respx.mock
@pytest.mark.asyncio
async def test_get_invoices(bamboorose_client: BambooroseClient):
    """Test that the get_invoices method constructs the correct SOAP request and returns the response."""
    request = respx.post("https://test.com").mock(
        return_value=httpx.Response(200, text="<xml>Success</xml>")
    )
    response = await bamboorose_client.get_invoices("2023-01-01T00:00:00Z")

    assert request.called
    assert response.status_code == 200
    assert response.text == "<xml>Success</xml>"
    soap_request = request.calls.last.request.content.decode("utf-8")
    assert "<ser:userName>test_user</ser:userName>" in soap_request
    assert "<ser:password>test_password</ser:password>" in soap_request
    assert "<ser:availableTimestamp>2023-01-01T00:00:00Z</ser:availableTimestamp>" in soap_request


@respx.mock
@pytest.mark.asyncio
async def test_get_invoices_retry_on_5xx(bamboorose_client: BambooroseClient):
    """Test that the get_invoices method retries on a 5xx error."""
    request = respx.post("https://test.com").mock(
        side_effect=[
            httpx.Response(500),
            httpx.Response(200, text="<xml>Success</xml>"),
        ]
    )
    response = await bamboorose_client.get_invoices("2023-01-01T00:00:00Z")

    assert request.call_count == 2
    assert response.status_code == 200
    assert response.text == "<xml>Success</xml>"


@respx.mock
@pytest.mark.asyncio
async def test_get_invoices_no_retry_on_4xx(bamboorose_client: BambooroseClient):
    """Test that the get_invoices method does not retry on a 4xx error."""
    request = respx.post("https://test.com").mock(
        side_effect=[
            httpx.Response(400),
            httpx.Response(200, text="<xml>Success</xml>"),
        ]
    )
    with pytest.raises(httpx.HTTPStatusError):
        await bamboorose_client.get_invoices("2023-01-01T00:00:00Z")

    assert request.call_count == 1
