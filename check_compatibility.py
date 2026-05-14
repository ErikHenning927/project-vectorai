#!/usr/bin/env python3
"""
Verifica compatibilidade de imagem contra o banco vetorial Pinecone
Retorna dados do produto se compatível
"""

import json
import logging
from PIL import Image
import requests
from io import BytesIO
from embeddings import EmbeddingGenerator
from pinecone_manager import PineconeManager
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

def check_image(image_source: str, threshold: float = 0.85, top_k: int = 5) -> dict:
    """
    Verifica compatibilidade de uma imagem usando Pinecone
    
    Args:
        image_source: URL ou caminho local da imagem
        threshold: Score mínimo de similaridade (0-1)
        top_k: Número de matches para retornar
    
    Returns:
        Dict com resultado (compatível, dados do produto, matches)
    """
    
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
    
    # Buscar no Pinecone
    try:
        pinecone_mgr = PineconeManager()
        results = pinecone_mgr.query_similarity(embedding.tolist(), top_k=top_k)
        
        if not results or not results['matches']:
            return {
                "status": "no_reference",
                "message": "Nenhuma referência encontrada no banco",
                "is_compatible": False,
                "matches": []
            }
        
        # O Pinecone com métrica Cosine retorna valores entre -1 e 1 (ou 0 e 1 para CLIP normalizado)
        best_match = results['matches'][0]
        best_score = float(best_match['score'])
        best_product = best_match['metadata']
        
        # Determinar status
        if best_score >= threshold:
            status = "compatible"
            message = "Imagem compatível"
        else:
            status = "incompatible"
            message = "Imagem não compatível"
            
        matches = []
        for match in results['matches']:
            matches.append({
                "score": float(match['score']),
                "product": match['metadata']
            })
            
        return {
            "status": status,
            "message": message,
            "is_compatible": best_score >= threshold,
            "score": best_score,
            "threshold": threshold,
            "product": best_product,
            "matches": matches
        }
        
    except Exception as e:
        return {"error": f"Erro ao consultar Pinecone: {e}"}

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python check_compatibility.py <imagem> [--threshold 0.85]")
        sys.exit(1)
    
    image_source = sys.argv[1]
    threshold = 0.85
    
    if "--threshold" in sys.argv:
        idx = sys.argv.index("--threshold")
        threshold = float(sys.argv[idx + 1])
    
    result = check_image(image_source, threshold=threshold)
    print(json.dumps(result, indent=2, ensure_ascii=False))
