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

CSV_PATH = "data/inventory.csv"

df = pd.read_csv(CSV_PATH)

print(f"CSV loaded: {len(df)} rows")


# ==========================================
# 3. Convert data types
# ==========================================

df["product_id"] = df["product_id"].astype(str)

df["date"] = pd.to_datetime(
    df["date"],
    format="mixed"
).dt.date

df["distribution_id"] = df["distribution_id"].astype(str)

df["stock_quantity"] = df["stock_quantity"].astype("int64")


# ==========================================
# 4. Select columns matching database schema
# ==========================================

columns = [
    "product_id",
    "date",
    "distribution_id",
    "stock_quantity",
]

df = df[columns]


# ==========================================
# 5. Show sample before loading
# ==========================================

print("\nSample data:")
print(df.head())

print("\nDate range:")
print(f"From: {df['date'].min()}")
print(f"To:   {df['date'].max()}")


# ==========================================
# 6. Load data into PostgreSQL
# ==========================================

df.to_sql(
    "inventory",
    engine,
    if_exists="append",
    index=False
)


# ==========================================
# 7. Finish
# ==========================================

print(
    f"\nSuccessfully loaded {len(df)} rows into inventory."
)