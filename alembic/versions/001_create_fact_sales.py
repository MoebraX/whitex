from alembic import op
import sqlalchemy as sa


revision = "001_create_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:

    # ============================================================
    # PRODUCTS
    # ============================================================
    op.create_table(
        "products",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "product_id",
            sa.String(length=50),
            nullable=False,
            unique=True,
        ),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("subcategory", sa.String(length=100), nullable=True),
        sa.Column("volume_ml", sa.Integer(), nullable=True),
        sa.Column("unit_price_rial", sa.BigInteger(), nullable=True),
        sa.Column("cost_price_rial", sa.BigInteger(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
    )


    # ============================================================
    # DISTRIBUTIONS
    # ============================================================
    op.create_table(
        "distributions",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "distribution_id",
            sa.String(length=50),
            nullable=False,
            unique=True,
        ),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("province", sa.String(length=100), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("region", sa.String(length=100), nullable=True),
    )


    # ============================================================
    # SALES
    # ============================================================
    op.create_table(
        "sales",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "sale_id",
            sa.String(length=50),
            nullable=False
        ),
        sa.Column(
            "date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "product_id",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "distribution_id",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "quantity",
            sa.BigInteger(),
            nullable=True,
        ),
        sa.Column(
            "unit_price_rial",
            sa.BigInteger(),
            nullable=True,
        ),
        sa.Column(
            "discount_percent",
            sa.Numeric(5, 2),
            nullable=True,
        ),
        sa.Column(
            "total_price_rial",
            sa.BigInteger(),
            nullable=True,
        ),
        sa.Column("is_consistent", sa.Boolean(), nullable=True),
    )


    # ============================================================
    # INVENTORY
    # ============================================================
    op.create_table(
        "inventory",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "product_id",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "distribution_id",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "stock_quantity",
            sa.BigInteger(),
            nullable=True,
        ),
    )


    # ============================================================
    # DATA CLEANING LOGS
    # ============================================================
    op.create_table(
        "data_cleaning_logs",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "sale_id",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "modified_field",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "before",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "after",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "flag",
            sa.String(length=100),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("data_cleaning_logs")
    op.drop_table("inventory")
    op.drop_table("sales")
    op.drop_table("distributions")
    op.drop_table("products")
