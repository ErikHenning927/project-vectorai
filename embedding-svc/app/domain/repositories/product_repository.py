from abc import ABC, abstractmethod
from typing import List

from app.domain.entities.product import Product


class IProductRepository(ABC):
    """Interface de repositório de produtos — define o contrato sem implementação."""

    @abstractmethod
    def get_all(self) -> List[Product]:
        """Retorna todos os produtos disponíveis."""
        raise NotImplementedError
