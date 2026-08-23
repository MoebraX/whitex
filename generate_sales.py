import csv
import random
from datetime import date, timedelta
from collections import defaultdict

# ============================================================
# CONFIG
# ============================================================

PRODUCTS_FILE = "products.csv"
REGIONS_FILE = "regions.csv"
OUTPUT_FILE = "sales.csv"

NUM_SALES = 50_000

START_DATE = date(2025, 8, 24)
END_DATE = date(2026, 8, 23)

random.seed(42)


# ============================================================
# BUSINESS WEIGHTS
# ============================================================

# Higher value = higher probability of being sold.
# Small-volume products intentionally have higher demand.

PRODUCT_WEIGHTS = {
    "P001": 2.0,   # Thick bleach 4L
    "P002": 3.5,   # Thick bleach 2L
    "P003": 8.0,   # Thick bleach 1L

    "P004": 3.0,   # Regular bleach 4L
    "P005": 10.0,  # Regular bleach 1L

    "P006": 5.0,   # Glass cleaner 1L
    "P007": 7.0,   # Glass cleaner 500ml

    "P008": 6.0,   # Toilet cleaner 1L
    "P009": 7.5,   # Toilet cleaner 750ml
    "P010": 4.5,   # Scented toilet cleaner 1L

    "P011": 5.0,   # Hand wash 2L
    "P012": 6.0,   # Hand wash 1L
    "P013": 7.5,   # Hand wash 500ml
    "P014": 4.0,   # Antibacterial hand wash 500ml

    "P015": 2.5,   # Dishwashing 4L
    "P016": 4.5,   # Dishwashing 2L
    "P017": 9.0,   # Dishwashing 1L
    "P018": 7.0,   # Dishwashing 750ml
    "P019": 4.0,   # Concentrated dishwashing 1L
    "P020": 6.0,   # Concentrated dishwashing 500ml
}


# Market size of regions.
# Larger cities have more transactions.

REGION_WEIGHTS = {
    "R001": 20.0,  # Tehran
    "R002": 9.0,   # Isfahan
    "R003": 12.0,  # Mashhad
    "R004": 7.0,   # Shiraz
    "R005": 7.0,   # Tabriz
    "R006": 8.0,   # Karaj
    "R007": 6.0,   # Ahvaz
    "R008": 4.0,   # Qom
    "R009": 5.0,   # Rasht
    "R010": 4.5,   # Sari
    "R011": 4.5,   # Kerman
    "R012": 3.5,   # Yazd
    "R013": 4.0,   # Urmia
    "R014": 3.5,   # Kermanshah
    "R015": 3.0,   # Bandar Abbas
}


# ============================================================
# HELPERS
# ============================================================

def daterange(start, end):
    """Generate every date between start and end."""
    current = start

    while current <= end:
        yield current
        current += timedelta(days=1)


def get_category_seasonality(category, month):
    """
    Returns a multiplier for the category/month combination.
    """

    multiplier = 1.0

    # Nowruz / spring cleaning
    if month == 12:
        if category == "bleach":
            multiplier *= 1.40
        elif category == "toilet_cleaner":
            multiplier *= 1.35
        elif category == "glass_cleaner":
            multiplier *= 1.30
        elif category == "dishwashing_liquid":
            multiplier *= 1.20
        elif category == "hand_wash":
            multiplier *= 1.10

    # Farvardin / Nowruz holidays
    elif month == 1:
        multiplier *= 0.85

    # Summer
    elif month in [4, 5]:
        if category == "glass_cleaner":
            multiplier *= 1.10
        elif category == "dishwashing_liquid":
            multiplier *= 1.08

    # School season
    elif month == 7:
        if category == "hand_wash":
            multiplier *= 1.10
        elif category == "dishwashing_liquid":
            multiplier *= 1.05

    # Winter
    elif month == 10:
        if category == "hand_wash":
            multiplier *= 1.05

    return multiplier


def get_day_multiplier(d):
    """
    Adds weekly purchasing behavior.
    """

    # Friday in Iran is typically lower business activity.
    if d.weekday() == 4:
        return 0.75

    # Thursday tends to be slightly higher.
    if d.weekday() == 3:
        return 1.10

    return 1.0


def get_distributor_quantity_multiplier(distributor_type):
    """
    Wholesale orders are larger but less frequent.
    """

    if distributor_type == "wholesaler":
        return 5.0

    if distributor_type == "supermarket":
        return 2.5

    if distributor_type == "direct":
        return 4.0

    # retailer
    return 1.0


def generate_quantity(distributor_type):
    """
    Generates realistic order quantities.
    """

    if distributor_type == "wholesaler":
        return random.randint(30, 300)

    if distributor_type == "supermarket":
        return random.randint(10, 100)

    if distributor_type == "direct":
        return random.randint(20, 200)

    # retailer
    return random.randint(3, 40)


def generate_discount(distributor_type, quantity):
    """
    Larger orders receive larger discounts.
    """

    if distributor_type == "wholesaler":
        if quantity >= 200:
            return random.choice([8, 10, 12, 15])
        elif quantity >= 100:
            return random.choice([5, 7, 8, 10])
        else:
            return random.choice([3, 5, 7])

    if distributor_type == "supermarket":
        return random.choice([2, 3, 5, 7])

    if distributor_type == "direct":
        return random.choice([3, 5, 7, 10])

    return random.choice([0, 0, 2, 3, 5])


# ============================================================
# LOAD PRODUCTS
# ============================================================

products = []

with open(PRODUCTS_FILE, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        row["unit_price_toman"] = int(row["unit_price_toman"])

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
# CREATE WEIGHTED LISTS
# ============================================================

product_weights = [
    PRODUCT_WEIGHTS.get(p["product_id"], 1.0)
    for p in products
]

region_weights = [
    REGION_WEIGHTS.get(r["region_id"], 1.0)
    for r in regions
]


# ============================================================
# GENERATE SALES
# ============================================================

sales = []

all_dates = list(daterange(START_DATE, END_DATE))

for sale_number in range(1, NUM_SALES + 1):

    # --------------------------------------------------------
    # Select date using seasonal weights
    # --------------------------------------------------------

    date_weights = []

    for d in all_dates:

        weight = get_day_multiplier(d)

        # Approximate seasonal uplift across the year.
        if d.month == 12:
            weight *= 1.30
        elif d.month == 1:
            weight *= 0.85
        elif d.month in [10, 11]:
            weight *= 1.05

        date_weights.append(weight)

    sale_date = random.choices(
        all_dates,
        weights=date_weights,
        k=1
    )[0]

    # --------------------------------------------------------
    # Select product
    # --------------------------------------------------------

    product = random.choices(
        products,
        weights=product_weights,
        k=1
    )[0]

    category = product["category"]

    # Category-specific seasonality
    seasonal_multiplier = get_category_seasonality(
        category,
        sale_date.month
    )

    # Occasionally skip seasonal effect.
    # This prevents the data from looking artificially perfect.
    if random.random() < 0.15:
        seasonal_multiplier = 1.0

    # --------------------------------------------------------
    # Select region
    # --------------------------------------------------------

    region = random.choices(
        regions,
        weights=region_weights,
        k=1
    )[0]

    distributor_type = region["distributor_type"]

    # --------------------------------------------------------
    # Quantity
    # --------------------------------------------------------

    quantity = generate_quantity(distributor_type)

    # Apply seasonal demand to quantity occasionally.
    if random.random() < 0.70:
        quantity = max(
            1,
            round(quantity * seasonal_multiplier)
        )

    # Random normal variation
    quantity = max(
        1,
        round(quantity * random.uniform(0.85, 1.20))
    )

    # --------------------------------------------------------
    # Price
    # --------------------------------------------------------

    base_price = product["unit_price_toman"]

    # Small realistic price variation.
    # Simulates different contracts / price changes.
    price_factor = random.uniform(0.97, 1.08)

    unit_price = round(base_price * price_factor)

    # --------------------------------------------------------
    # Discount
    # --------------------------------------------------------

    discount_percent = generate_discount(
        distributor_type,
        quantity
    )

    gross_price = quantity * unit_price

    total_price = round(
        gross_price * (1 - discount_percent / 100)
    )

    sale = {
        "sale_id": f"S{sale_number:06d}",
        "date": sale_date.isoformat(),
        "product_id": product["product_id"],
        "region_id": region["region_id"],
        "quantity": quantity,
        "unit_price_toman": unit_price,
        "discount_percent": discount_percent,
        "total_price_toman": total_price,
    }

    sales.append(sale)


# ============================================================
# ADD CONTROLLED DIRTY DATA
# ============================================================

num_dirty = round(NUM_SALES * 0.025)

dirty_indices = random.sample(
    range(NUM_SALES),
    num_dirty
)

for index in dirty_indices:

    row = sales[index]

    error_type = random.choices(
        [
            "missing_region",
            "invalid_product",
            "negative_quantity",
            "invalid_discount",
            "date_format",
            "extra_spaces",
            "duplicate",
            "missing_price",
            "comma_number"
        ],
        weights=[
            10,
            8,
            4,
            3,
            10,
            8,
            7,
            5,
            5
        ],
        k=1
    )[0]

    if error_type == "missing_region":
        row["region_id"] = ""

    elif error_type == "invalid_product":
        row["product_id"] = "P999"

    elif error_type == "negative_quantity":
        row["quantity"] = -random.randint(1, 10)

    elif error_type == "invalid_discount":
        row["discount_percent"] = random.choice([50, 75, 100, 110])

    elif error_type == "date_format":
        d = row["date"]
        row["date"] = d.replace("-", "/")

    elif error_type == "extra_spaces":
        row["product_id"] = f' {row["product_id"]} '

    elif error_type == "duplicate":
        if index > 0:
            previous = sales[index - 1]
            row.update(previous)

    elif error_type == "missing_price":
        row["unit_price_toman"] = ""

    elif error_type == "comma_number":
        row["total_price_toman"] = (
            f'{row["total_price_toman"]:,}'
        )


# ============================================================
# WRITE CSV
# ============================================================

fieldnames = [
    "sale_id",
    "date",
    "product_id",
    "region_id",
    "quantity",
    "unit_price_toman",
    "discount_percent",
    "total_price_toman",
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
    writer.writerows(sales)


print(f"Generated {len(sales):,} sales records.")
print(f"Output: {OUTPUT_FILE}")