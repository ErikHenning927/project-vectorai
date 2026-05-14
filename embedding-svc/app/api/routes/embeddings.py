"""
Router: /embeddings

POST /embeddings/generate  — dispara a geração de embeddings para todos os produtos
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.dependencies import get_generate_embeddings_use_case
from app.application.use_cases.generate_embeddings import (
    GenerateEmbeddingsUseCase,
    GenerateEmbeddingsResult,
)

router = APIRouter(prefix="/embeddings", tags=["embeddings"])


class GenerateEmbeddingsResponse(BaseModel):
    total_input: int
    total_processed: int
    total_failed: int
    success: bool
    message: str


@router.post(
    "/generate",
    response_model=GenerateEmbeddingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Gerar embeddings de produtos",
    description=(
        "Busca todos os produtos do banco, gera embeddings via CLIP "
        "e envia ao Pinecone. Opera de forma síncrona."
    ),
)
def generate_embeddings(
    namespace: str = "default",
    use_case: GenerateEmbeddingsUseCase = Depends(get_generate_embeddings_use_case),
) -> GenerateEmbeddingsResponse:
    result: GenerateEmbeddingsResult = use_case.execute(namespace=namespace)

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha ao gerar ou enviar embeddings. Verifique os logs.",
        )

    return GenerateEmbeddingsResponse(
        total_input=result.total_input,
        total_processed=result.total_processed,
        total_failed=result.total_failed,
        success=result.success,
        message=f"{result.total_processed} embeddings gerados e enviados ao Pinecone.",
    )
