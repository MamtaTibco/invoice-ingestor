from x35_settings.fastapi import FastAPISettings
from x35_settings.uvicorn import UvicornSettings


class Settings:
    """
    Unified settings class combining Base, FastAPI, and Uvicorn settings.

    Provides a single point of access to all configuration.
    """

    def __init__(self):
        self.fastapi = FastAPISettings()
        self.uvicorn = UvicornSettings()


settings = Settings()
