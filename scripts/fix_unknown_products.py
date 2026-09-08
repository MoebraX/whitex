import psycopg2


conn = psycopg2.connect(
    host="localhost",
    port=5434,
    database="whitex",
    user="whitex",
    password="whitex_password"
)

cursor = conn.cursor()


# ------------------------------------------------------------
# 1. Create UNKNOWN product
# ------------------------------------------------------------

cursor.execute("""
INSERT INTO products
(
    product_id,
    name,
    category,
    subcategory,
    volume_ml,
    unit_price_rial,
    cost_price_rial,
    is_active
)
VALUES
(
    'UNKNOWN',
    'محصول نامشخص',
    'unknown',
    'unknown',
    NULL,
    0,
    0,
    false
)
ON CONFLICT (product_id) DO NOTHING;
""")


# ------------------------------------------------------------
# 2. Find invalid product ids
# ------------------------------------------------------------

cursor.execute("""
SELECT DISTINCT product_id
FROM sales
WHERE product_id IS NOT NULL
AND product_id NOT IN (
    SELECT product_id
    FROM products
);
""")


invalid_products = cursor.fetchall()


print("Invalid products:")
for item in invalid_products:
    print(item[0])


# ------------------------------------------------------------
# 3. Replace invalid ids with UNKNOWN
# ------------------------------------------------------------

cursor.execute("""
UPDATE sales
SET product_id = 'UNKNOWN'
WHERE product_id IS NOT NULL
AND product_id NOT IN (
    SELECT product_id
    FROM products
);
""")


updated_rows = cursor.rowcount


conn.commit()


print(
    f"Updated {updated_rows} sales rows to UNKNOWN product"
)


cursor.close()
conn.close()