from alembic import op
import sqlalchemy as sa


revision = "002_fix_tables_for_bi"
down_revision = "001_create_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:

    # ============================================================
    # SALES FIXES
    # ============================================================

    # sale_id باید unique باشد چون شناسه تراکنش است
    op.create_unique_constraint(
        "uq_sales_sale_id",
        "sales",
        ["sale_id"]
    )


    # ارتباط فروش با محصول
    op.create_foreign_key(
        "fk_sales_product",
        "sales",
        "products",
        ["product_id"],
        ["product_id"]
    )


    # ارتباط فروش با مرکز توزیع
    op.create_foreign_key(
        "fk_sales_distribution",
        "sales",
        "distributions",
        ["distribution_id"],
        ["distribution_id"]
    )


    # ============================================================
    # INVENTORY FIXES
    # ============================================================

    # تضمین ارتباط موجودی با محصول
    op.create_foreign_key(
        "fk_inventory_product",
        "inventory",
        "products",
        ["product_id"],
        ["product_id"]
    )


    # تضمین ارتباط موجودی با مرکز توزیع
    op.create_foreign_key(
        "fk_inventory_distribution",
        "inventory",
        "distributions",
        ["distribution_id"],
        ["distribution_id"]
    )


    # جلوگیری از ثبت موجودی تکراری برای یک محصول،
    # یک مرکز و یک تاریخ
    op.create_unique_constraint(
        "uq_inventory_product_date_distribution",
        "inventory",
        [
            "product_id",
            "date",
            "distribution_id"
        ]
    )


    # ============================================================
    # PRODUCTS FIXES
    # ============================================================

    # قیمت و هزینه نباید منفی باشند
    op.create_check_constraint(
        "ck_products_price_positive",
        "products",
        """
        unit_price_rial >= 0
        AND cost_price_rial >= 0
        """
    )


    # ============================================================
    # SALES VALIDATION
    # ============================================================

    # تعداد فروش منفی منطقی نیست
    op.create_check_constraint(
        "ck_sales_quantity_positive",
        "sales",
        """
        quantity >= 0
        """
    )


    # تخفیف باید بین 0 تا 100 باشد
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
        "ck_sales_quantity_positive",
        "sales",
        type_="check"
    )

    op.drop_constraint(
        "ck_products_price_positive",
        "products",
        type_="check"
    )

    op.drop_constraint(
        "uq_inventory_product_date_distribution",
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

    op.drop_constraint(
        "uq_sales_sale_id",
        "sales",
        type_="unique"
    )