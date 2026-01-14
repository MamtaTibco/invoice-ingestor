
### Interacting with External Services

When a service needs to communicate with an external API, it's best to encapsulate the logic in a dedicated client class.

-   **HTTP Client**: Use the `httpx` library for making asynchronous HTTP requests. Configure it with appropriate timeouts, connection limits, and retries.
-   **Client Class**: Create a class that handles the specifics of the external API, such as URL construction and request/response formatting. This class should be configured using settings from the `x35-settings` library.

    ```python
    # Example of a generic API client
    import httpx
    from settings.settings import settings

    class ExternalServiceClient:
        def __init__(self):
            self.base_url = settings.external_api_url
            self.timeout = settings.external_api_timeout

        async def submit_data(self, data: dict):
            async with httpx.AsyncClient() as client:
                # ... make request ...

    external_client = ExternalServiceClient()
    ```
