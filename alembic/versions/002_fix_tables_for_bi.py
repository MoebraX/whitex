from alembic import op
import sqlalchemy as sa


revision = "002_fix_tables_for_bi"
down_revision = "001_create_tables"

branch_labels = None
depends_on = None



def upgrade() -> None:


    # ============================================================
    # SALES RELATIONSHIPS
    # ============================================================

    op.create_foreign_key(
        "fk_sales_product",
        "sales",
        "products",
        ["product_id"],
        ["product_id"]
    )


    op.create_foreign_key(
        "fk_sales_distribution",
        "sales",
        "distributions",
        ["distribution_id"],
        ["distribution_id"]
    )



    # ============================================================
    # INVENTORY RELATIONSHIPS
    # ============================================================

    op.create_foreign_key(
        "fk_inventory_product",
        "inventory",
        "products",
        ["product_id"],
        ["product_id"]
    )


    op.create_foreign_key(
        "fk_inventory_distribution",
        "inventory",
        "distributions",
        ["distribution_id"],
        ["distribution_id"]
    )



    # ============================================================
    # INVENTORY UNIQUENESS
    # ============================================================

    op.create_unique_constraint(
        "uq_inventory_daily_snapshot",
        "inventory",
        [
            "product_id",
            "distribution_id",
            "date"
        ]
    )



    # ============================================================
    # DATA VALIDATION
    # ============================================================

    op.create_check_constraint(
        "ck_products_positive_prices",
        "products",
        """
        unit_price_rial >= 0
        AND cost_price_rial >= 0
        """
    )


    op.create_check_constraint(
        "ck_sales_positive_quantity",
        "sales",
        """
        quantity >= 0
        """
    )


    op.create_check_constraint(
        "ck_sales_discount_range",
        "sales",
        """
        discount_percent >= 0
        AND discount_percent <= 100
        """
    )



def downgrade() -> None:


    op.drop_constraint(
        "ck_sales_discount_range",
        "sales",
        type_="check"
    )


    op.drop_constraint(
        "ck_sales_positive_quantity",
        "sales",
        type_="check"
    )


    op.drop_constraint(
        "ck_products_positive_prices",
        "products",
        type_="check"
    )


    op.drop_constraint(
        "uq_inventory_daily_snapshot",
        "inventory",
        type_="unique"
    )


    op.drop_constraint(
        "fk_inventory_distribution",
        "inventory",
        type_="foreignkey"
    )


    op.drop_constraint(
        "fk_inventory_product",
        "inventory",
        type_="foreignkey"
    )


    op.drop_constraint(
        "fk_sales_distribution",
        "sales",
        type_="foreignkey"
    )


    op.drop_constraint(
        "fk_sales_product",
        "sales",
        type_="foreignkey"
    )