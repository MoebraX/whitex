import pandas as pd
from sqlalchemy import create_engine

from src.config import DATABASE_URL


# ==========================================
# 1. Database connection
# ==========================================

engine = create_engine(DATABASE_URL)


# ==========================================
# 2. Read cleaned CSV
# ==========================================

CSV_PATH = "data/clean_sales.csv"

df = pd.read_csv(CSV_PATH)

print(f"CSV loaded: {len(df)} rows")


# ==========================================
# 3. Rename columns
# ==========================================

df = df.rename(columns={
    "date": "sale_date"
})


# ==========================================
# 4. Convert Gregorian date
# ==========================================

df["sale_date"] = pd.to_datetime(
    df["sale_date"],
    errors="coerce"
).dt.date


# ==========================================
# 5. Validate dates
# ==========================================

invalid_dates = df["sale_date"].isna().sum()

if invalid_dates > 0:
    raise ValueError(
        f"Found {invalid_dates} invalid or missing sale_date values."
    )


# ==========================================
# 6. Convert data types
# ==========================================

df["sale_id"] = df["sale_id"].astype("int64")
df["quantity"] = df["quantity"].astype("int64")
df["unit_price_rial"] = df["unit_price_rial"].astype("int64")
df["discount_percent"] = df["discount_percent"].astype(float)
df["total_price_rial"] = df["total_price_rial"].astype("int64")


# ==========================================
# 7. Remove data-cleaning validation column
# ==========================================

if "is_consistent" in df.columns:
    df = df.drop(columns=["is_consistent"])


# ==========================================
# 8. Show sample before loading
# ==========================================

print("\nSample data:")
print(df.head())

print("\nDate range:")
print(f"From: {df['sale_date'].min()}")
print(f"To:   {df['sale_date'].max()}")


# ==========================================
# 9. Load data into PostgreSQL
# ==========================================

df.to_sql(
    "fact_sales",
    engine,
    if_exists="append",
    index=False
)


# ==========================================
# 10. Finish
# ==========================================

print(
    f"\nSuccessfully loaded {len(df)} rows into fact_sales."
)
