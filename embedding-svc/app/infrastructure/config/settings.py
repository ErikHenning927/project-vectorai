import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Configurações do microserviço lidas via variáveis de ambiente."""

    # ── PostgreSQL ──────────────────────────────────────────────────────────
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_NAME: str = os.getenv("DB_NAME", "vectorai")

    # ── CLIP Embedding ──────────────────────────────────────────────────────
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "ViT-B-32")
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "32"))

    # ── Pinecone ────────────────────────────────────────────────────────────
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "vectorai-index")
    PINECONE_HOST: str = os.getenv("PINECONE_HOST", "")

    # ── API ─────────────────────────────────────────────────────────────────
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8001"))

    @classmethod
    def get_db_url(cls) -> str:
        """URL de conexão para SQLAlchemy / Alembic."""
        return (
            f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}"
            f"@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        )

    @classmethod
    def get_psycopg2_params(cls) -> dict:
        """Parâmetros de conexão para psycopg2."""
        return {
            "dbname": cls.DB_NAME,
            "user": cls.DB_USER,
            "password": cls.DB_PASSWORD,
            "host": cls.DB_HOST,
            "port": cls.DB_PORT,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
