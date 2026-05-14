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
        "url": "https://images.samsung.com/is/image/samsung/p6pim/br/qn65s85fagxzd/gallery/br-oled-tv-qn65s85fagxzd-front-graphite-548309472?$1164_776_PNG$",
        "internal_code": "QN65S85FAGXZD",
        "name": "Vision AI TV 65 polegadas OLED 4K S85F 2025",
        "reference": "TV-OLED",
        "category_name": "TVS",
    },
    {
        "url": (
            "https://images.samsung.com/is/image/samsung/p6pim/br/feature/165645774/br-feature-samsung-book-543711019?$FB_TYPE_A_JPG$"
        ),
        "internal_code": "GB4PRO",
        "name": "Galaxy Book4 Pro",
        "reference": "Galaxy Book4 Pro",
        "category_name": "NOTEBOOKS",
    },
    {
        "url": "https://images.samsung.com/is/image/samsung/p6pim/br/f2507/gallery/br-galaxy-watch8-l320-sm-l320nzspzto-547659627?$1164_776_PNG$",
        "internal_code": "GW8-40BLT",
        "name": "Galaxy Watch8 (Bluetooth, 40 mm)",
        "reference": "Galaxy Watch8 (Bluetooth, 40 mm)",
        "category_name": "WEARABLES",
    },
    {
        "url": "https://images.samsung.com/is/image/samsung/p6pim/br/sm-a576bzaezto/gallery/br-galaxy-a57-5g-sm-a576-sm-a576bzaezto-551768727?$1164_776_PNG$",
        "internal_code": "GALAXY A57 5G (128GB)",
        "name": "Galaxy A57 5G (128GB)",
        "reference": "Galaxy A57 5G",
        "category_name": "SMARTPHONES",
    }
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
