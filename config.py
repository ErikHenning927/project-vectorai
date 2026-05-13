import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuração da aplicação"""
    
    # PostgreSQL
    DB_TYPE = os.getenv("DB_TYPE", "postgres")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_NAME = os.getenv("DB_NAME", "vectorai")
    
    # Embedding
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "ViT-B/32")  # Modelo CLIP padrão
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))
    
    # Storage
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")
    EMBEDDINGS_FILE = os.getenv("EMBEDDINGS_FILE", "embeddings.npz")
    
    @classmethod
    def get_connection_params(cls):
        """Retorna parâmetros de conexão para psycopg2"""
        return {
            "dbname": cls.DB_NAME,
            "user": cls.DB_USER,
            "password": cls.DB_PASSWORD,
            "host": cls.DB_HOST,
            "port": cls.DB_PORT
        }

    @classmethod
    def get_connection_string(cls):
        """Retorna a string de conexão baseada no DB_TYPE"""
        if cls.DB_TYPE == "mssql":
            DB_INSTANCE = os.getenv("DB_INSTANCE")
            return f"Driver={{ODBC Driver 18 for SQL Server}};Server={cls.DB_HOST}\\{DB_INSTANCE};Database={cls.DB_NAME};UID={cls.DB_USER};PWD={cls.DB_PASSWORD};TrustServerCertificate=yes"
        elif cls.DB_TYPE == "postgres":
            return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        raise ValueError(f"Tipo de banco de dados não suportado: {cls.DB_TYPE}")
