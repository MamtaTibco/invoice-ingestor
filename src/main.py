# -*- coding: utf-8 -*-
"""Application entrypoint."""
import uvicorn

from src.app import create_app
from src.settings.config import get_settings

app = create_app()
settings = get_settings()

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.fastapi.host,
        port=settings.fastapi.port,
        reload=settings.fastapi.reload,
    )