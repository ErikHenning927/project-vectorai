import logging
from dataclasses import dataclass
from typing import Protocol, List, Any

import numpy as np

from app.domain.entities.product import Product
from app.domain.repositories.product_repository import IProductRepository
from app.domain.repositories.vector_repository import IVectorRepository

logger = logging.getLogger(__name__)


class IEmbeddingService(Protocol):
    """Protocolo para o serviço de geração de embeddings."""

    def process_batch(self, products: List[Product]) -> tuple[List[Product], np.ndarray]:
        """Processa produtos e retorna os bem-sucedidos com seus embeddings."""
        ...


@dataclass
class GenerateEmbeddingsResult:
    """Resultado da execução do use case."""

    total_input: int
    total_processed: int
    total_failed: int

    @property
    def success(self) -> bool:
        return self.total_processed > 0


class GenerateEmbeddingsUseCase:
    """
    Orquestra a geração de embeddings de produtos e envio ao vector store.

    Fluxo:
      1. Busca produtos via IProductRepository
      2. Gera embeddings via IEmbeddingService
      3. Limpa dados antigos no vector store
      4. Envia novos vetores via IVectorRepository
    """

    def __init__(
        self,
        product_repo: IProductRepository,
        vector_repo: IVectorRepository,
        embedding_service: IEmbeddingService,
    ):
        self._product_repo = product_repo
        self._vector_repo = vector_repo
        self._embedding_service = embedding_service

    def execute(self, namespace: str = "default") -> GenerateEmbeddingsResult:
        logger.info("=== GenerateEmbeddingsUseCase: iniciando ===")

        # 1. Buscar produtos
        products = self._product_repo.get_all()
        total_input = len(products)
        logger.info(f"Produtos encontrados: {total_input}")

        if total_input == 0:
            logger.warning("Nenhum produto encontrado no banco.")
            return GenerateEmbeddingsResult(
                total_input=0, total_processed=0, total_failed=0
            )

        # 2. Gerar embeddings
        processed_products, embeddings = self._embedding_service.process_batch(products)
        total_processed = len(processed_products)
        total_failed = total_input - total_processed
        logger.info(f"Embeddings gerados: {total_processed}/{total_input}")

        if total_processed == 0:
            logger.error("Nenhum embedding gerado — abortando.")
            return GenerateEmbeddingsResult(
                total_input=total_input,
                total_processed=0,
                total_failed=total_failed,
            )

        # 3. Limpar dados antigos
        logger.info("Limpando vetores antigos no Pinecone...")
        self._vector_repo.delete_all(namespace=namespace)

        # 4. Upsert
        logger.info(f"Enviando {total_processed} vetores ao Pinecone...")
        ok = self._vector_repo.upsert(processed_products, embeddings, namespace=namespace)

        if ok:
            logger.info(f"✓ Concluído: {total_processed} vetores enviados")
        else:
            logger.error("Falha ao enviar vetores")

        return GenerateEmbeddingsResult(
            total_input=total_input,
            total_processed=total_processed if ok else 0,
            total_failed=total_failed if ok else total_input,
        )
