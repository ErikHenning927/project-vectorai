import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from typing import List
from config import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gerenciador de conexão com PostgreSQL"""
    
    def __init__(self):
        self.connection_params = Config.get_connection_params()
        self.connection = None
    
    def connect(self):
        """Conecta ao banco de dados PostgreSQL"""
        try:
            logger.info(f"Conectando ao PostgreSQL em {self.connection_params['host']}...")
            self.connection = psycopg2.connect(**self.connection_params)
            self.connection.autocommit = True
            logger.info("Conexão estabelecida com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar ao PostgreSQL: {e}")
            return False
    
    def disconnect(self):
        """Desconecta do banco de dados"""
        if self.connection:
            self.connection.close()
            logger.info("Conexão fechada")
    
    def initialize_db(self):
        """Inicializa a estrutura do banco de dados"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            with self.connection.cursor() as cursor:
                logger.info("Criando tabelas...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        id SERIAL PRIMARY KEY,
                        url TEXT NOT NULL,
                        internal_code TEXT,
                        name TEXT,
                        reference TEXT,
                        category_name TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                logger.info("Tabelas criadas com sucesso")
                return True
        except Exception as e:
            logger.error(f"Erro ao inicializar banco: {e}")
            return False

    def seed_data(self, products: List[dict]):
        """Popula o banco com dados iniciais para teste"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            with self.connection.cursor() as cursor:
                logger.info(f"Inserindo {len(products)} produtos...")
                for p in products:
                    cursor.execute("""
                        INSERT INTO products (url, internal_code, name, reference, category_name)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING;
                    """, (p['url'], p.get('internal_code'), p.get('name'), p.get('reference'), p.get('category_name')))
                logger.info("Dados inseridos com sucesso")
                return True
        except Exception as e:
            logger.error(f"Erro ao popular banco: {e}")
            return False

    def get_product_data(self, query: str = None) -> List[dict]:
        """
        Busca dados de produtos do banco de dados
        
        Args:
            query: Query SQL customizada
        
        Returns:
            Lista de dicionários com dados do produto
        """
        if not self.connection:
            if not self.connect():
                return []
        
        if query is None:
            query = "SELECT url, internal_code, name, reference, category_name FROM products"
        
        try:
            logger.info(f"Executando query no PostgreSQL...")
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                # Converter de RealDictRow para dict comum
                results = [dict(row) for row in results]
            
            logger.info(f"Encontrados {len(results)} produtos")
            return results
        except Exception as e:
            logger.error(f"Erro ao executar query: {e}")
            return []
