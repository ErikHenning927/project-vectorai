import logging
from typing import List, Any

from pinecone import Pinecone

from app.domain.entities.product import Product
from app.domain.repositories.vector_repository import IVectorRepository
from app.infrastructure.config.settings import Settings

logger = logging.getLogger(__name__)


class PineconeVectorRepository(IVectorRepository):
    """Implementação concreta de IVectorRepository usando a SDK do Pinecone."""

    def __init__(self, settings: Settings):
        if not settings.PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY não configurada no .env")

        pc = Pinecone(api_key=settings.PINECONE_API_KEY)

        if settings.PINECONE_HOST:
            self._index = pc.Index(host=settings.PINECONE_HOST)
        else:
            self._index = pc.Index(settings.PINECONE_INDEX_NAME)

        logger.info(f"Conectado ao índice Pinecone: {settings.PINECONE_INDEX_NAME}")

    # ── IVectorRepository ────────────────────────────────────────────────────

    def upsert(
        self, products: List[Product], embeddings: Any, namespace: str = "default"
    ) -> bool:
        vectors = [
            {
                "id": product.vector_id,
                "values": embeddings[idx].tolist(),
                "metadata": {
                    "name": product.name or "",
                    "url": product.url,
                    "reference": product.reference or "",
                    "category": product.category_name or "",
                },
            }
            for idx, product in enumerate(products)
        ]

        try:
            logger.info(f"Fazendo upsert de {len(vectors)} vetores...")
            self._index.upsert(vectors=vectors, namespace=namespace)
            logger.info("Upsert concluído com sucesso")
            return True
        except Exception as exc:
            logger.error(f"Erro no upsert: {exc}")
            return False

    def delete_all(self, namespace: str = "default") -> bool:
        """Remove todos os vetores do namespace via delete_all=True."""
        try:
            self._index.delete(delete_all=True, namespace=namespace)
            logger.info(f"Vetores do namespace '{namespace}' removidos")
            return True
        except Exception as exc:
            logger.error(f"Erro ao deletar vetores: {exc}")
            return False

    def query_similarity(
        self,
        vector: List[float],
        top_k: int = 5,
        namespace: str = "default",
    ) -> Any:
        try:
            return self._index.query(
                vector=vector,
                top_k=top_k,
                include_metadata=True,
                namespace=namespace,
            )
        except Exception as exc:
            logger.error(f"Erro na query: {exc}")
            return None
