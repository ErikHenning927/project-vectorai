#!/usr/bin/env python3
"""
Gera embeddings de produtos do SQL Server
"""

import logging
import os
from pathlib import Path
from config import Config
from database import DatabaseManager
from embeddings import EmbeddingGenerator
from pinecone_manager import PineconeManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('poc.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    """Gera embeddings para produtos do banco de dados"""
    
    logger.info("Iniciando geração de embeddings...")
    
    try:
        # Conectar ao banco
        logger.info("Conectando ao PostgreSQL...")
        db = DatabaseManager()
        if not db.connect():
            logger.error("Falha ao conectar")
            return False
        
        # Buscar dados de produtos
        logger.info("Buscando dados de produtos...")
        products = db.get_product_data()
        
        if not products:
            logger.error("Nenhum produto encontrado")
            return False
        
        db.disconnect()
        
        # Gerar embeddings
        logger.info(f"Processando {len(products)} produtos...")
        generator = EmbeddingGenerator()
        products_list, embeddings = generator.process_products_batch(products)
        
        if len(products_list) == 0:
            logger.error("Nenhum embedding foi gerado")
            return False
        
        # Salvar no Pinecone
        logger.info("Limpando dados antigos no Pinecone...")
        pinecone_mgr = PineconeManager()
        pinecone_mgr.delete_all_vectors()
        
        logger.info("Enviando para o Pinecone...")
        success = pinecone_mgr.upsert_vectors(products_list, embeddings)
        
        if success:
            logger.info(f"✓ Concluído: {len(products_list)} produtos enviados para o Pinecone")
        else:
            logger.error("Falha ao enviar dados para o Pinecone")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Erro: {e}")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
