import logging
from typing import List

import psycopg2
from psycopg2.extras import RealDictCursor

from app.domain.entities.product import Product
from app.domain.repositories.product_repository import IProductRepository
from app.infrastructure.config.settings import Settings

logger = logging.getLogger(__name__)


class PostgresProductRepository(IProductRepository):
    """Implementação concreta de IProductRepository usando psycopg2 + PostgreSQL."""

    def __init__(self, settings: Settings):
        self._params = settings.get_psycopg2_params()
        self._conn = None

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def _connect(self) -> None:
        if self._conn and not self._conn.closed:
            return
        logger.info(f"Conectando ao PostgreSQL em {self._params['host']}...")
        self._conn = psycopg2.connect(**self._params)
        self._conn.autocommit = True
        logger.info("Conexão estabelecida")

    def disconnect(self) -> None:
        if self._conn and not self._conn.closed:
            self._conn.close()
            logger.info("Conexão encerrada")

    # ── IProductRepository ───────────────────────────────────────────────────

    def get_all(self) -> List[Product]:
        self._connect()
        sql = """
            SELECT url, internal_code, name, reference, category_name
            FROM products
        """
        try:
            with self._conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                rows = cur.fetchall()
            products = [Product(**dict(row)) for row in rows]
            logger.info(f"Encontrados {len(products)} produtos")
            return products
        except Exception as exc:
            logger.error(f"Erro ao buscar produtos: {exc}")
            return []
