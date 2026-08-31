import pandas as pd
import jdatetime
from sqlalchemy import create_engine

from src.config import DB_PORT, DATABASE_URL


# ==========================================
# 1. Database connection
# ==========================================

engine = create_engine(DATABASE_URL)


# ==========================================
# 2. Read CSV
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
# 4. Convert Jalali date → Gregorian date
# ==========================================

def jalali_to_gregorian(date):
    if pd.isna(date):
        return None

    date = str(date).strip()

    year, month, day = map(int, date.split("-"))

    return jdatetime.date(
        year,
        month,
        day
    ).togregorian()


df["sale_date"] = df["sale_date"].apply(jalali_to_gregorian)


# ==========================================
# 5. Convert data types
# ==========================================

df["sale_id"] = df["sale_id"].astype("int64")
df["quantity"] = df["quantity"].astype("int64")
df["unit_price_rial"] = df["unit_price_rial"].astype("int64")
df["discount_percent"] = df["discount_percent"].astype(float)
df["total_price_rial"] = df["total_price_rial"].astype("int64")


# ==========================================
# 6. Remove data-cleaning validation column
# ==========================================

if "is_consistent" in df.columns:
    df = df.drop(columns=["is_consistent"])


# ==========================================
# 7. Show sample before loading
# ==========================================

print("\nSample data:")
print(df.head())

print("\nDate range:")
print(f"From: {df['sale_date'].min()}")
print(f"To:   {df['sale_date'].max()}")


# ==========================================
# 8. Load data into PostgreSQL
# ==========================================

df.to_sql(
    "fact_sales",
    engine,
    if_exists="append",
    index=False
)


# ==========================================
# 9. Finish
# ==========================================

print(f"\nSuccessfully loaded {len(df)} rows into fact_sales.")