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

CSV_PATH = "data/distributions.csv"

df = pd.read_csv(CSV_PATH)

print(f"CSV loaded: {len(df)} rows")


# ==========================================
# 3. Convert data types
# ==========================================

df["distribution_id"] = df["distribution_id"].astype(str)

# address can contain empty values
df["address"] = df["address"].astype("string")

df["province"] = df["province"].astype("string")

df["city"] = df["city"].astype("string")

df["region"] = df["region"].astype("string")


# ==========================================
# 4. Select columns matching database schema
# ==========================================

columns = [
    "distribution_id",
    "address",
    "province",
    "city",
    "region",
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
    "distributions",
    engine,
    if_exists="append",
    index=False
)


# ==========================================
# 7. Finish
# ==========================================

print(
    f"\nSuccessfully loaded {len(df)} rows into distributions."
)