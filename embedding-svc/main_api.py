#!/usr/bin/env python3
"""
Entrypoint da API HTTP — inicia o servidor Uvicorn.

Uso:
  cd embedding-svc
  python main_api.py
  # ou
  uvicorn app.api.server:app --host 0.0.0.0 --port 8000 --reload
"""

import uvicorn
from app.infrastructure.config.settings import Settings
from app.api.server import app  # noqa: F401 — garante registro dos routers

if __name__ == "__main__":
    settings = Settings()
    uvicorn.run(
        "app.api.server:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False,
        log_level="info",
    )
