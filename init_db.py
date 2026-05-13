import logging
from database import DatabaseManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_and_seed():
    db = DatabaseManager()
    
    # 1. Initialize structure
    if not db.initialize_db():
        logger.error("Falha ao inicializar o banco")
        return
    
    # 2. Seed some data
    sample_products = [
        {
            'url': 'https://samsungbr.vtexassets.com/arquivos/ids/331011/image.png',
            'internal_code': 'NP750XDA-KF2BR',
            'name': 'Samsung Book Core i5-1135G7',
            'reference': 'Samsung Book',
            'category_name': 'Notebooks'
        },
        {
            'url': 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/macbook-air-silver-select-201810?wid=900&hei=900&fmt=jpeg&qlt=90&.v=1633027804000',
            'internal_code': 'MGN63BZ/A',
            'name': 'MacBook Air M1 13-inch',
            'reference': 'MacBook Air',
            'category_name': 'Notebooks'
        },
        {
            'url': 'https://samsungbr.vtexassets.com/arquivos/ids/310118/image.png',
            'internal_code': 'NP930XDB-KF1BR',
            'name': 'Samsung Galaxy Book Pro',
            'reference': 'Galaxy Book Pro',
            'category_name': 'Notebooks'
        }
    ]
    
    if db.seed_data(sample_products):
        logger.info("Banco inicializado e populado com sucesso!")
    else:
        logger.error("Falha ao popular o banco")
    
    db.disconnect()

if __name__ == "__main__":
    init_and_seed()
