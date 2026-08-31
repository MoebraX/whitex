from alembic import op
import sqlalchemy as sa


revision = "001_create_fact_sales"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "fact_sales",
        sa.Column("sale_id", sa.Integer(), nullable=True),
        sa.Column("sale_date", sa.Date(), nullable=True),
        sa.Column("product_id", sa.String(length=10), nullable=True),
        sa.Column("distribution_id", sa.String(length=10), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=True),
        sa.Column("unit_price_rial", sa.BigInteger(), nullable=True),
        sa.Column("discount_percent", sa.Numeric(5, 2), nullable=True),
        sa.Column("total_price_rial", sa.BigInteger(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("fact_sales")