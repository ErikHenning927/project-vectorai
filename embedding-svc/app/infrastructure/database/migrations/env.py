"""Alembic environment configuration.

Equivalente ao ormconfig / datasource do TypeORM:
  - Lê a DATABASE_URL via Settings
  - Suporta migrações online (com conexão ativa) e offline (gera SQL)
"""

import sys
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Garantir que o pacote `app` seja encontrado independente de onde alembic é chamado
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))

from app.infrastructure.config.settings import Settings
from app.infrastructure.database.models import Base

# --------------------------------------------------------------------------- #
# Alembic Config                                                               #
# --------------------------------------------------------------------------- #
config = context.config

# Configurar logging a partir do alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Sobrescrever a URL de conexão com a lida do .env
config.set_main_option("sqlalchemy.url", Settings.get_db_url())

# Metadata dos modelos ORM — o --autogenerate compara isso com o banco
target_metadata = Base.metadata


# --------------------------------------------------------------------------- #
# Run migrations                                                               #
# --------------------------------------------------------------------------- #

def run_migrations_offline() -> None:
    """Gera SQL sem precisar de conexão ativa (equivalente ao --dry-run do TypeORM)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa as migrations com uma conexão real ao banco."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
