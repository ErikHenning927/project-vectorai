#!/usr/bin/env python3
"""
Entrypoint CLI — executa a geração de embeddings sem passar pela API HTTP.

Uso:
  cd embedding-svc
  python main.py
"""

import logging
import sys

from app.infrastructure.config.settings import Settings
from app.infrastructure.database.postgres_adapter import PostgresProductRepository
from app.infrastructure.embedding.clip_adapter import ClipEmbeddingService
from app.infrastructure.vector_store.pinecone_adapter import PineconeVectorRepository
from app.application.use_cases.generate_embeddings import GenerateEmbeddingsUseCase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("embedding-svc.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def main() -> None:
    settings = Settings()

    use_case = GenerateEmbeddingsUseCase(
        product_repo=PostgresProductRepository(settings),
        vector_repo=PineconeVectorRepository(settings),
        embedding_service=ClipEmbeddingService(settings),
    )

    result = use_case.execute()

    if result.success:
        logger.info(
            f"✓ Concluído — {result.total_processed}/{result.total_input} produtos processados"
        )
        sys.exit(0)
    else:
        logger.error("✗ Falha — verifique os logs para detalhes")
        sys.exit(1)


if __name__ == "__main__":
    main()
