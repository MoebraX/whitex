import pandas as pd
from sqlalchemy import create_engine


# ==========================================
# 1. Database connection
# ==========================================

DATABASE_URL = (
    "postgresql+psycopg2://"
    "whitex:whitex_password@localhost:5432/whitex"
)

engine = create_engine(DATABASE_URL)


# ==========================================
# 2. Read CSV
# ==========================================

CSV_PATH = "data/sale.csv"

df = pd.read_csv(CSV_PATH)

print(f"CSV loaded: {len(df)} rows")


# ==========================================
# 3. Rename columns
# ==========================================

df = df.rename(columns={
    "date": "sale_date"
})


# ==========================================
# 4. Convert data types
# ==========================================

df["sale_date"] = pd.to_datetime(df["sale_date"]).dt.date

df["sale_id"] = df["sale_id"].astype("int64")
df["quantity"] = df["quantity"].astype("int64")
df["unit_price_rial"] = df["unit_price_rial"].astype("int64")
df["discount_percent"] = df["discount_percent"].astype(float)
df["total_price_rial"] = df["total_price_rial"].astype("int64")


# ==========================================
# 5. Load data into PostgreSQL
# ==========================================

df.to_sql(
    "fact_sales",
    engine,
    if_exists="append",
    index=False
)


# ==========================================
# 6. Finish
# ==========================================

print(f"Successfully loaded {len(df)} rows into fact_sales.")