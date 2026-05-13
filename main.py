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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('poc.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    """Gera embeddings para produtos do banco de dados"""
    
    logger.info("Iniciando geração de embeddings...")
    
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    embeddings_file = os.path.join(Config.OUTPUT_DIR, Config.EMBEDDINGS_FILE)
    
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
        
        # Salvar
        logger.info("Salvando...")
        generator.save_embeddings_with_data(products_list, embeddings, embeddings_file)
        
        logger.info(f"✓ Concluído: {len(products_list)} produtos com embeddings")
        logger.info(f"Arquivo: {embeddings_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro: {e}")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
