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

# df = df.rename(columns={
#     "date": "date"
# })


# ==========================================
# 4. Convert Gregorian date
# ==========================================

# def jalali_to_gregorian(date):
#     if pd.isna(date):
#         return None

#     date = str(date).strip()

#     year, month, day = map(int, date.split("-"))

#     return jdatetime.date(
#         year,
#         month,
#         day
#     ).togregorian()


# df["date"] = df["date"].apply(jalali_to_gregorian)


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

# if "is_consistent" in df.columns:
#     df = df.drop(columns=["is_consistent"])


# ==========================================
# 8. Show sample before loading
# ==========================================

print("\nSample data:")
print(df.head())

print("\nDate range:")
print(f"From: {df['date'].min()}")
print(f"To:   {df['date'].max()}")


# ==========================================
# 9. Load data into PostgreSQL
# ==========================================

df.to_sql(
    "sales",
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
