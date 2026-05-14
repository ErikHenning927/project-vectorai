"""
Script de seed — popula a tabela products com dados iniciais.

Equivalente ao seed do TypeORM:
  typeorm-seeding seed

Uso:
  cd embedding-svc
  python scripts/seed.py

É idempotente: usa ON CONFLICT DO NOTHING com base no internal_code.
"""

import logging
import sys
import os

import psycopg2

# Garantir que o pacote app seja encontrado
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.infrastructure.config.settings import Settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ── Dados iniciais ────────────────────────────────────────────────────────────

SEED_PRODUCTS = [
    {
        "url": "https://samsungbr.vtexassets.com/arquivos/ids/331011/image.png",
        "internal_code": "NP750XDA-KF2BR",
        "name": "Samsung Book Core i5-1135G7",
        "reference": "Samsung Book",
        "category_name": "Notebooks",
    },
    {
        "url": (
            "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/"
            "macbook-air-silver-select-201810?wid=900&hei=900&fmt=jpeg&qlt=90&.v=1633027804000"
        ),
        "internal_code": "MGN63BZ/A",
        "name": "MacBook Air M1 13-inch",
        "reference": "MacBook Air",
        "category_name": "Notebooks",
    },
    {
        "url": "https://samsungbr.vtexassets.com/arquivos/ids/310118/image.png",
        "internal_code": "NP930XDB-KF1BR",
        "name": "Samsung Galaxy Book Pro",
        "reference": "Galaxy Book Pro",
        "category_name": "Notebooks",
    },
]


# ── Seed function ─────────────────────────────────────────────────────────────

def run_seed() -> None:
    settings = Settings()
    logger.info("Conectando ao PostgreSQL...")
    conn = psycopg2.connect(**settings.get_psycopg2_params())
    conn.autocommit = True

    try:
        with conn.cursor() as cur:
            logger.info(f"Inserindo {len(SEED_PRODUCTS)} produtos (idempotente)...")
            for product in SEED_PRODUCTS:
                cur.execute(
                    """
                    INSERT INTO products (url, internal_code, name, reference, category_name)
                    VALUES (%(url)s, %(internal_code)s, %(name)s, %(reference)s, %(category_name)s)
                    ON CONFLICT (internal_code) DO NOTHING
                    """,
                    product,
                )
            logger.info("✓ Seed concluído com sucesso!")
    except Exception as exc:
        logger.error(f"Erro no seed: {exc}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    run_seed()
