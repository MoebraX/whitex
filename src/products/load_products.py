import pandas as pd
from sqlalchemy import create_engine

from src.config import DATABASE_URL


# ==========================================
# 1. Database connection
# ==========================================

engine = create_engine(DATABASE_URL)


# ==========================================
# 2. Read CSV
# ==========================================

CSV_PATH = "data/products.csv"

df = pd.read_csv(CSV_PATH)

print(f"CSV loaded: {len(df)} rows")


# ==========================================
# 3. Convert data types
# ==========================================

df["product_id"] = df["product_id"].astype(str)

df["name"] = df["name"].astype("string")

df["category"] = df["category"].astype("string")

df["subcategory"] = df["subcategory"].astype("string")

df["volume_ml"] = df["volume_ml"].astype("int64")

df["unit_price_rial"] = df["unit_price_rial"].astype("int64")

df["cost_price_rial"] = df["cost_price_rial"].astype("int64")

df["is_active"] = df["is_active"].astype(bool)


# ==========================================
# 4. Select columns matching database schema
# ==========================================

columns = [
    "product_id",
    "name",
    "category",
    "subcategory",
    "volume_ml",
    "unit_price_rial",
    "cost_price_rial",
    "is_active",
]

df = df[columns]


# ==========================================
# 5. Show sample before loading
# ==========================================

print("\nSample data:")
print(df.head())


# ==========================================
# 6. Load data into PostgreSQL
# ==========================================

df.to_sql(
    "products",
    engine,
    if_exists="append",
    index=False
)


# ==========================================
# 7. Finish
# ==========================================

print(
    f"\nSuccessfully loaded {len(df)} rows into products."
)