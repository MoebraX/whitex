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

CSV_PATH = "data/data_cleaning_logs.csv"

df = pd.read_csv(CSV_PATH)

print(f"CSV loaded: {len(df)} rows")


# ==========================================
# 3. Convert data types
# ==========================================

# sale_id is VARCHAR(50) in PostgreSQL
df["sale_id"] = df["sale_id"].astype(str)

# date is TIMESTAMP-like data in the CSV,
# but the database column is DATE
df["date"] = pd.to_datetime(df["date"]).dt.date


# ==========================================
# 4. Select columns matching database schema
# ==========================================

columns = [
    "sale_id",
    "date",
    "modified_field",
    "before",
    "after",
    "flag",
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
    "data_cleaning_logs",
    engine,
    if_exists="append",
    index=False
)


# ==========================================
# 7. Finish
# ==========================================

print(
    f"\nSuccessfully loaded {len(df)} rows into data_cleaning_logs."
)