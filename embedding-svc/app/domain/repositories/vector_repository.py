from abc import ABC, abstractmethod
from typing import List, Any

from app.domain.entities.product import Product


class IVectorRepository(ABC):
    """Interface do vector store — define o contrato sem implementação."""

    @abstractmethod
    def upsert(self, products: List[Product], embeddings: Any, namespace: str = "default") -> bool:
        """Insere ou atualiza vetores no vector store."""
        raise NotImplementedError

    @abstractmethod
    def delete_all(self, namespace: str = "default") -> bool:
        """Remove todos os vetores de um namespace."""
        raise NotImplementedError

    @abstractmethod
    def query_similarity(
        self,
        vector: List[float],
        top_k: int = 5,
        namespace: str = "default",
    ) -> Any:
        """Busca vetores similares ao vetor informado."""
        raise NotImplementedError
