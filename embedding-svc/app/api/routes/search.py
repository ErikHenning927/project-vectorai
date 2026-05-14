"""
Router: /search

POST /search/by-image  — busca produtos similares a uma imagem (via URL)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, HttpUrl

from app.api.dependencies import get_embedding_service, get_vector_repo
from app.infrastructure.embedding.clip_adapter import ClipEmbeddingService
from app.infrastructure.vector_store.pinecone_adapter import PineconeVectorRepository

router = APIRouter(prefix="/search", tags=["search"])


class SearchByImageRequest(BaseModel):
    image_url: HttpUrl
    top_k: int = 5
    namespace: str = "default"


class SearchMatch(BaseModel):
    id: str
    score: float
    metadata: dict


class SearchByImageResponse(BaseModel):
    query_url: str
    matches: list[SearchMatch]


@router.post(
    "/by-image",
    response_model=SearchByImageResponse,
    summary="Busca por similaridade de imagem",
    description=(
        "Recebe a URL de uma imagem, gera seu embedding com CLIP "
        "e retorna os produtos mais similares do Pinecone."
    ),
)
def search_by_image(
    body: SearchByImageRequest,
    embedding_svc: ClipEmbeddingService = Depends(get_embedding_service),
    vector_repo: PineconeVectorRepository = Depends(get_vector_repo),
) -> SearchByImageResponse:
    # Gerar embedding da imagem de query
    emb = embedding_svc.embed_image_url(str(body.image_url))
    if emb is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Não foi possível processar a imagem. Verifique a URL.",
        )

    # Buscar similares no Pinecone
    results = vector_repo.query_similarity(
        vector=emb.tolist(),
        top_k=body.top_k,
        namespace=body.namespace,
    )

    if results is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Erro ao consultar o Pinecone.",
        )

    matches = [
        SearchMatch(
            id=m["id"],
            score=round(m["score"], 4),
            metadata=m.get("metadata", {}),
        )
        for m in results.get("matches", [])
    ]

    return SearchByImageResponse(
        query_url=str(body.image_url),
        matches=matches,
    )
