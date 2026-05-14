"""create products table

Revision ID: 0001
Revises:
Create Date: 2026-05-14

Equivalente ao migration gerado pelo TypeORM:
  typeorm migration:generate -n CreateProductsTable
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Cria a tabela products — equivalente ao migration:run do TypeORM."""
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("internal_code", sa.Text(), nullable=True),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("reference", sa.Text(), nullable=True),
        sa.Column("category_name", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("internal_code", name="uq_products_internal_code"),
    )
    # Índice para busca rápida por código interno
    op.create_index("ix_products_internal_code", "products", ["internal_code"])


def downgrade() -> None:
    """Reverte a criação da tabela — equivalente ao migration:revert do TypeORM."""
    op.drop_index("ix_products_internal_code", table_name="products")
    op.drop_table("products")
