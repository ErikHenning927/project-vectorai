"""
Modelos SQLAlchemy — camada de infraestrutura.

Equivalente às @Entity do TypeORM. É aqui que você altera colunas
para que o `alembic revision --autogenerate` detecte as mudanças.

NÃO confundir com app/domain/entities/product.py (dataclass puro de domínio).
"""

from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    Numeric,
    Text,
    TIMESTAMP,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class ProductModel(Base):
    """
    Mapeamento ORM da tabela `products`.

    Para adicionar/alterar colunas:
      1. Edite este arquivo (ex: adicione `description = Column(Text)`)
      2. Rode: alembic revision --autogenerate -m "add description to products"
      3. Rode: alembic upgrade head
    """

    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("internal_code", name="uq_products_internal_code"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text, nullable=False)
    internal_code = Column(Text, nullable=True)
    name = Column(Text, nullable=True)
    reference = Column(Text, nullable=True)
    category_name = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)

    # ── Exemplo: descomente, rode --autogenerate e veja a migration gerada ──
    # description = Column(Text, nullable=True)
    # price = Column(Numeric(10, 2), nullable=True)
    # is_active = Column(Boolean, nullable=False, server_default="TRUE")
