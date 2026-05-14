"""
FastAPI application factory.

Monta o app com todos os routers registrados e middleware de logging.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import embeddings, search

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="embedding-svc",
        description=(
            "Microserviço de embeddings vetoriais de imagens de produtos. "
            "Utiliza CLIP para geração e Pinecone como vector store."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── CORS ─────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(embeddings.router)
    app.include_router(search.router)

    # ── Health check ─────────────────────────────────────────────────────────
    @app.get("/health", tags=["health"])
    def health() -> dict:
        return {"status": "ok", "service": "embedding-svc"}

    logger.info("embedding-svc iniciado")
    return app


app = create_app()
