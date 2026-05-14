import logging
from pinecone import Pinecone
from config import Config
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class PineconeManager:
    """Gerenciador de integração com Pinecone"""
    
    def __init__(self):
        if not Config.PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY não configurada no .env")
        
        self.pc = Pinecone(api_key=Config.PINECONE_API_KEY)
        self.index_name = Config.PINECONE_INDEX_NAME
        self.host = Config.PINECONE_HOST
        
        # Conectar ao índice
        try:
            if self.host:
                self.index = self.pc.Index(host=self.host)
            else:
                self.index = self.pc.Index(self.index_name)
            logger.info(f"Conectado ao índice Pinecone: {self.index_name}")
        except Exception as e:
            logger.error(f"Erro ao conectar ao Pinecone: {e}")
            raise

    def upsert_vectors(self, products: List[Dict[str, Any]], embeddings: Any, namespace: str = "default"):
        """
        Envia vetores e metadados para o Pinecone
        
        Args:
            products: Lista de dicionários com metadados
            embeddings: Array numpy de embeddings
            namespace: Namespace opcional
        """
        vectors_to_upsert = []
        
        for idx, product in enumerate(products):
            # O Pinecone exige um ID (usaremos o internal_code ou URL como fallback)
            vector_id = product.get('internal_code') or str(hash(product['url']))
            
            vectors_to_upsert.append({
                "id": vector_id,
                "values": embeddings[idx].tolist(),
                "metadata": {
                    "name": product.get('name', ''),
                    "url": product.get('url', ''),
                    "reference": product.get('reference', ''),
                    "category": product.get('category_name', '')
                }
            })
        
        try:
            logger.info(f"Fazendo upsert de {len(vectors_to_upsert)} vetores para o Pinecone...")
            self.index.upsert(vectors=vectors_to_upsert, namespace=namespace)
            logger.info("Upsert concluído com sucesso!")
            return True
        except Exception as e:
            logger.error(f"Erro no upsert: {e}")
            return False

    def query_similarity(self, vector: List[float], top_k: int = 5, namespace: str = "default"):
        """
        Busca vetores similares
        
        Args:
            vector: Vetor de busca (lista de floats)
            top_k: Número de resultados
            namespace: Namespace
        """
        try:
            results = self.index.query(
                vector=vector,
                top_k=top_k,
                include_metadata=True,
                namespace=namespace
            )
            return results
        except Exception as e:
            logger.error(f"Erro na query do Pinecone: {e}")
            return None
