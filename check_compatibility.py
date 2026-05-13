#!/usr/bin/env python3
"""
Verifica compatibilidade de imagem contra embeddings salvos
Retorna dados do produto se compatível
"""

import numpy as np
import json
import logging
from pathlib import Path
from PIL import Image
import requests
from io import BytesIO
from embeddings import EmbeddingGenerator
from config import Config

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def load_image(source: str):
    """Carrega imagem de URL ou arquivo local"""
    try:
        if source.startswith('http'):
            response = requests.get(source, timeout=10)
            response.raise_for_status()
            return Image.open(BytesIO(response.content)).convert("RGB")
        else:
            return Image.open(source).convert("RGB")
    except Exception as e:
        logger.error(f"Erro ao carregar imagem: {e}")
        return None

def check_image(image_source: str, threshold: float = 0.7, top_n: int = 5) -> dict:
    """
    Verifica compatibilidade de uma imagem
    
    Args:
        image_source: URL ou caminho local da imagem
        threshold: Score mínimo de similaridade (0-1)
        top_n: Número de matches para retornar
    
    Returns:
        Dict com resultado (compatível, dados do produto, matches)
    """
    
    # Carregar dados salvos
    embeddings_file = Path(Config.OUTPUT_DIR) / Config.EMBEDDINGS_FILE
    if not embeddings_file.exists():
        return {"error": f"Arquivo não encontrado: {embeddings_file}"}
    
    try:
        data = np.load(embeddings_file, allow_pickle=True)
        reference_embeddings = data['embeddings']
        products = json.loads(str(data['products_json']))
    except Exception as e:
        return {"error": f"Erro ao carregar dados: {e}"}
    
    # Normalizar embeddings de referência
    embeddings_norm = reference_embeddings / np.linalg.norm(
        reference_embeddings, axis=1, keepdims=True
    )
    
    # Carregar e processar imagem
    image = load_image(image_source)
    if image is None:
        return {"error": "Falha ao carregar imagem"}
    
    # Gerar embedding
    try:
        generator = EmbeddingGenerator()
        embedding = generator.generate_embedding(image)
        if embedding is None:
            return {"error": "Falha ao gerar embedding"}
    except Exception as e:
        return {"error": f"Erro ao gerar embedding: {e}"}
    
    # Normalizar embedding
    embedding_norm = embedding / np.linalg.norm(embedding)
    
    # Calcular similaridade
    similarities = embeddings_norm @ embedding_norm
    
    # Encontrar melhor match
    best_idx = np.argmax(similarities)
    best_score = float(similarities[best_idx])
    best_product = products[best_idx]
    
    # Determinar status
    if best_score < 0.5:
        status = "no_reference"
        message = "Nenhuma referência similar encontrada"
    elif best_score >= threshold:
        status = "compatible"
        message = "Imagem compatível"
    else:
        status = "incompatible"
        message = "Imagem não compatível"
    
    # Compatíveis (acima do threshold)
    compatible_mask = similarities >= threshold
    compatible_indices = np.argsort(-similarities[compatible_mask])[:top_n]
    
    compatible_matches = []
    for idx in compatible_indices:
        if similarities[idx] >= threshold:
            compatible_matches.append({
                "score": float(similarities[idx]),
                "product": products[idx]
            })
    
    return {
        "status": status,
        "message": message,
        "is_compatible": best_score >= threshold,
        "score": best_score,
        "threshold": threshold,
        "product": best_product,
        "compatible_count": int(np.sum(similarities >= threshold)),
        "matches": compatible_matches
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python check_compatibility.py <imagem> [--threshold 0.7]")
        sys.exit(1)
    
    image_source = sys.argv[1]
    threshold = 0.7
    
    if "--threshold" in sys.argv:
        idx = sys.argv.index("--threshold")
        threshold = float(sys.argv[idx + 1])
    
    result = check_image(image_source, threshold=threshold)
    print(json.dumps(result, indent=2, ensure_ascii=False))
