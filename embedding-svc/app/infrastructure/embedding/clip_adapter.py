import logging
from io import BytesIO
from typing import List, Tuple

import numpy as np
import open_clip
import requests
import torch
from PIL import Image

from app.domain.entities.product import Product
from app.infrastructure.config.settings import Settings

logger = logging.getLogger(__name__)


class ClipEmbeddingService:
    """
    Adaptador de geração de embeddings usando o modelo CLIP (open_clip).
    Satisfaz o protocolo IEmbeddingService do use case.
    """

    def __init__(self, settings: Settings):
        model_name = settings.EMBEDDING_MODEL.replace("/", "-")
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Device: {self._device} | Modelo: {model_name}")

        self._model, _, self._preprocess = open_clip.create_model_and_transforms(
            model_name,
            pretrained="openai",
            device=self._device,
        )
        self._model.eval()
        logger.info("Modelo CLIP carregado com sucesso")

    # ── Internal helpers ────────────────────────────────────────────────────

    def _download_image(self, url: str) -> Image.Image | None:
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return Image.open(BytesIO(resp.content)).convert("RGB")
        except Exception as exc:
            logger.warning(f"Erro ao baixar imagem {url}: {exc}")
            return None

    def _embed(self, image: Image.Image) -> np.ndarray | None:
        try:
            tensor = self._preprocess(image).unsqueeze(0).to(self._device)
            with torch.no_grad():
                features = self._model.encode_image(tensor)
                features = features / features.norm(dim=-1, keepdim=True)
            return features.cpu().numpy().squeeze()
        except Exception as exc:
            logger.error(f"Erro ao gerar embedding: {exc}")
            return None

    # ── IEmbeddingService protocol ──────────────────────────────────────────

    def process_batch(
        self, products: List[Product]
    ) -> Tuple[List[Product], np.ndarray]:
        """Processa a lista de produtos e retorna apenas os bem-sucedidos."""
        ok_products: List[Product] = []
        ok_embeddings: List[np.ndarray] = []
        total = len(products)

        for idx, product in enumerate(products, 1):
            logger.info(f"Processando {idx}/{total}: {product.url}")
            image = self._download_image(product.url)
            if image is None:
                logger.warning(f"Pulando produto: {product.internal_code}")
                continue

            emb = self._embed(image)
            if emb is not None:
                ok_products.append(product)
                ok_embeddings.append(emb)
                logger.info("✓ OK")
            else:
                logger.warning(f"✗ Falha no embedding: {product.url}")

        logger.info(f"Total processado: {len(ok_products)}/{total}")
        return ok_products, np.array(ok_embeddings)

    def embed_image_url(self, url: str) -> np.ndarray | None:
        """Gera embedding de uma única URL de imagem (usado pela API de busca)."""
        image = self._download_image(url)
        if image is None:
            return None
        return self._embed(image)
