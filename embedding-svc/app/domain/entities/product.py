from dataclasses import dataclass
from typing import Optional


@dataclass
class Product:
    """Entidade de domínio que representa um produto."""

    url: str
    internal_code: Optional[str] = None
    name: Optional[str] = None
    reference: Optional[str] = None
    category_name: Optional[str] = None

    def __post_init__(self):
        if not self.url:
            raise ValueError("Product.url cannot be empty")

    @property
    def vector_id(self) -> str:
        """ID único para uso no vector store."""
        return self.internal_code or str(hash(self.url))
