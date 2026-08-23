import csv
import random
from datetime import date, timedelta
from collections import defaultdict

PRODUCTS_FILE = "products.csv"
REGIONS_FILE = "regions.csv"
OUTPUT_FILE = "inventory.csv"

START_DATE = date(2025, 8, 24)
END_DATE = date(2026, 8, 23)

random.seed(42)


# ============================================================
# LOAD PRODUCTS
# ============================================================

products = []

with open(PRODUCTS_FILE, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        products.append(row)


# ============================================================
# LOAD REGIONS
# ============================================================

regions = []

with open(REGIONS_FILE, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        regions.append(row)


# ============================================================
# BUSINESS WEIGHTS
# ============================================================

PRODUCT_DEMAND = {
    "P001": 0.7,
    "P002": 1.0,
    "P003": 2.0,

    "P004": 0.8,
    "P005": 2.5,

    "P006": 1.3,
    "P007": 1.8,

    "P008": 1.4,
    "P009": 1.7,
    "P010": 1.1,

    "P011": 1.2,
    "P012": 1.5,
    "P013": 1.9,
    "P014": 1.0,

    "P015": 0.7,
    "P016": 1.1,
    "P017": 2.2,
    "P018": 1.7,
    "P019": 1.0,
    "P020": 1.5,
}


REGION_SIZE = {
    "R001": 2.5,
    "R002": 1.5,
    "R003": 1.8,
    "R004": 1.3,
    "R005": 1.3,
    "R006": 1.5,
    "R007": 1.2,
    "R008": 0.9,
    "R009": 1.0,
    "R010": 0.9,
    "R011": 0.9,
    "R012": 0.7,
    "R013": 0.8,
    "R014": 0.8,
    "R015": 0.7,
}


# ============================================================
# DATE RANGE
# ============================================================

def daterange(start, end):

    current = start

    while current <= end:
        yield current
        current += timedelta(days=1)


# ============================================================
# GENERATE INVENTORY
# ============================================================

inventory = []

for product in products:

    product_id = product["product_id"]

    product_factor = PRODUCT_DEMAND.get(
        product_id,
        1.0
    )

    for region in regions:

        region_id = region["region_id"]

        region_factor = REGION_SIZE.get(
            region_id,
            1.0
        )

        # Initial stock
        base_stock = int(
            random.uniform(100, 500)
            * product_factor
            * region_factor
        )

        current_stock = base_stock

        for current_date in daterange(
            START_DATE,
            END_DATE
        ):

            # ------------------------------------------------
            # Seasonal restocking
            # ------------------------------------------------

            if current_date.month == 12:
                restock_multiplier = 1.4

            elif current_date.month in [1, 2]:
                restock_multiplier = 0.9

            else:
                restock_multiplier = 1.0

            # ------------------------------------------------
            # Random daily inventory movement
            # ------------------------------------------------

            daily_change = random.randint(
                -30,
                20
            )

            current_stock += daily_change

            # ------------------------------------------------
            # Periodic warehouse replenishment
            # ------------------------------------------------

            if current_date.day in [1, 15]:

                replenishment = int(
                    random.uniform(50, 200)
                    * product_factor
                    * region_factor
                    * restock_multiplier
                )

                current_stock += replenishment

            # ------------------------------------------------
            # Prevent negative inventory normally
            # ------------------------------------------------

            current_stock = max(
                0,
                current_stock
            )

            inventory.append({
                "product_id": product_id,
                "date": current_date.isoformat(),
                "region_id": region_id,
                "stock_quantity": current_stock
            })


# ============================================================
# ADD SMALL AMOUNT OF DIRTY DATA
# ============================================================

# num_dirty = round(len(inventory) * 0.01)

# dirty_indices = random.sample(
#     range(len(inventory)),
#     num_dirty
# )

# for index in dirty_indices:

#     row = inventory[index]

#     error_type = random.choice([
#         "negative_stock",
#         "missing_stock",
#         "date_format",
#         "duplicate",
#         "extra_spaces"
#     ])

#     if error_type == "negative_stock":
#         row["stock_quantity"] = -random.randint(1, 50)

#     elif error_type == "missing_stock":
#         row["stock_quantity"] = ""

#     elif error_type == "date_format":
#         row["date"] = row["date"].replace("-", "/")

#     elif error_type == "duplicate":
#         if index > 0:
#             row.update(inventory[index - 1])

#     elif error_type == "extra_spaces":
#         row["product_id"] = f' {row["product_id"]} '


# ============================================================
# WRITE CSV
# ============================================================

fieldnames = [
    "product_id",
    "date",
    "region_id",
    "stock_quantity",
]

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(inventory)


print(f"Generated {len(inventory):,} inventory records.")
print(f"Output: {OUTPUT_FILE}")