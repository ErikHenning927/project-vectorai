"""
Dependency injection container para FastAPI.

Instancia as dependências uma única vez (singleton por processo)
e as injeta nos routers via Depends().
"""

from functools import lru_cache

from app.infrastructure.config.settings import Settings
from app.infrastructure.database.postgres_adapter import PostgresProductRepository
from app.infrastructure.embedding.clip_adapter import ClipEmbeddingService
from app.infrastructure.vector_store.pinecone_adapter import PineconeVectorRepository
from app.application.use_cases.generate_embeddings import GenerateEmbeddingsUseCase


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


@lru_cache(maxsize=1)
def get_product_repo() -> PostgresProductRepository:
    return PostgresProductRepository(get_settings())


@lru_cache(maxsize=1)
def get_embedding_service() -> ClipEmbeddingService:
    return ClipEmbeddingService(get_settings())


@lru_cache(maxsize=1)
def get_vector_repo() -> PineconeVectorRepository:
    return PineconeVectorRepository(get_settings())


@lru_cache(maxsize=1)
def get_generate_embeddings_use_case() -> GenerateEmbeddingsUseCase:
    return GenerateEmbeddingsUseCase(
        product_repo=get_product_repo(),
        vector_repo=get_vector_repo(),
        embedding_service=get_embedding_service(),
    )
