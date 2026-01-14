# -*- coding: utf-8 -*-
"""Client for interacting with the Bamboorose SOAP API."""
import backoff
import httpx
from src.settings.config import get_settings


def _should_give_up(e: httpx.HTTPStatusError) -> bool:
    """Return True if the exception is not a 5xx error."""
    return e.response.status_code < 500


class BambooroseClient:
    """A client for interacting with the Bamboorose SOAP API."""

    def __init__(self) -> None:
        """Initializes the Bamboorose client."""
        settings = get_settings()
        self.base_url = settings.bamboorose.api_url
        self.timeout = settings.bamboorose.api_timeout
        self.username = settings.bamboorose.api_username
        self.password = settings.bamboorose.api_password.get_secret_value()

    @backoff.on_exception(
        backoff.expo,
        httpx.HTTPStatusError,
        max_tries=5,
        giveup=_should_give_up,
    )
    async def get_invoices(self, available_timestamp: str) -> httpx.Response:
        """
        Fetches invoices from the Bamboorose API.

        Args:
            available_timestamp: The timestamp to use for the request.

        Returns:
            The response from the API.
        """
        soap_request = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ser="http://services.bamboorose.com">
           <soapenv:Header/>
           <soapenv:Body>
              <ser:getCommercialInvoicesByAvailableTimestamp>
                 <ser:userName>{self.username}</ser:userName>
                 <ser:password>{self.password}</ser:password>
                 <ser:availableTimestamp>{available_timestamp}</ser:availableTimestamp>
              </ser:getCommercialInvoicesByAvailableTimestamp>
           </soapenv:Body>
        </soapenv:Envelope>
        """
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "getCommercialInvoicesByAvailableTimestamp",
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                content=soap_request,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
        return response


def get_bamboorose_client() -> BambooroseClient:
    """
    Returns an instance of the Bamboorose client.

    This function is used to inject the client into the application.
    """
    return BambooroseClient()
