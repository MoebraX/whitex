import csv
import random
from datetime import date, timedelta
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

LOGS_FILE = BASE_DIR / "data" / "data_cleaning_logs.csv"
PRODUCTS_FILE = BASE_DIR / "data" / "products.csv"
DISTRIBUTORS_FILE = BASE_DIR / "data" / "distributions.csv"
OUTPUT_FILE = BASE_DIR / "data" / "sales.csv"

NUM_SALES = 50_000

START_DATE = date(2025, 8, 24)
END_DATE = date(2026, 8, 23)

random.seed(42)


# ============================================================
# VALID PRODUCT IDs
# ============================================================

VALID_PRODUCT_IDS = {
    f"P{i:03d}"
    for i in range(1, 21)
}


# ============================================================
# VALID DISTRIBUTION IDs
# ============================================================

VALID_DISTRIBUTION_IDS = {
    f"D{i:03d}"
    for i in range(1, 37)
}


# ============================================================
# PRODUCT SALES WEIGHTS
# ============================================================

# Higher value = higher probability of being sold.
#
# Small-volume products intentionally have higher demand.
# For example:
#
#   1L bleach >> 4L bleach

PRODUCT_WEIGHTS = {
    "P001": 2.0,
    "P002": 3.5,
    "P003": 8.0,

    "P004": 3.0,
    "P005": 10.0,

    "P006": 5.0,
    "P007": 7.0,

    "P008": 6.0,
    "P009": 7.5,
    "P010": 4.5,

    "P011": 5.0,
    "P012": 6.0,
    "P013": 7.5,
    "P014": 4.0,

    "P015": 2.5,
    "P016": 4.5,
    "P017": 9.0,
    "P018": 7.0,
    "P019": 4.0,
    "P020": 6.0,
}


# ============================================================
# DISTRIBUTION / REGION WEIGHTS
# ============================================================

# Larger markets receive more sales transactions.

REGION_WEIGHTS = {
    "D001": 20.0,
    "D002": 9.0,
    "D003": 12.0,
    "D004": 7.0,
    "D005": 7.0,
    "D006": 8.0,
    "D007": 6.0,
    "D008": 4.0,
    "D009": 5.0,
    "D010": 4.5,
    "D011": 4.5,
    "D012": 3.5,
    "D013": 4.0,
    "D014": 3.5,
    "D015": 3.0,

    "D016": 3.0,
    "D017": 2.8,
    "D018": 2.8,
    "D019": 2.5,
    "D020": 2.5,
    "D021": 2.3,
    "D022": 2.3,
    "D023": 2.0,
    "D024": 2.0,
    "D025": 1.8,
    "D026": 1.8,
    "D027": 1.6,
    "D028": 1.6,
    "D029": 1.5,
    "D030": 1.5,
    "D031": 1.4,
    "D032": 1.4,
    "D033": 1.3,
    "D034": 1.3,
    "D035": 1.2,
    "D036": 1.2,
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


def gregorian_to_jalali(gy, gm, gd):
    """
    Convert Gregorian date to Jalali date.

    Returns:
        (jy, jm, jd)
    """

    g_d_m = [
        0, 31, 59, 90, 120, 151,
        181, 212, 243, 273, 304, 334
    ]

    if gy > 1600:
        jy = 979
        gy -= 1600
    else:
        jy = 0
        gy -= 621

    if gm > 2:
        gy2 = gy + 1
    else:
        gy2 = gy

    days = (
        365 * gy
        + (gy2 + 3) // 4
        - (gy2 + 99) // 100
        + (gy2 + 399) // 400
        - 80
        + gd
        + g_d_m[gm - 1]
    )

    if gm > 2 and (
        gy % 4 == 0
        and (
            gy % 100 != 0
            or gy % 400 == 0
        )
    ):
        days += 1

    jy += 33 * (days // 12053)
    days %= 12053

    jy += 4 * (days // 1461)
    days %= 1461

    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365

    if days < 186:
        jm = 1 + days // 31
        jd = 1 + days % 31
    else:
        jm = 7 + (days - 186) // 30
        jd = 1 + (days - 186) % 30

    return jy, jm, jd


# ============================================================
# CATEGORY SEASONALITY
# ============================================================

def get_category_seasonality(category, jalali_month):
    """
    Business seasonality based on Iranian calendar.

    Esfand:
        House cleaning / Nowruz preparation.

    Farvardin:
        Nowruz holidays.
    """

    multiplier = 1.0

    # --------------------------------------------------------
    # Esfand
    # --------------------------------------------------------

    if jalali_month == 12:

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

    # --------------------------------------------------------
    # Farvardin
    # --------------------------------------------------------

    elif jalali_month == 1:

        multiplier *= 0.85

    # --------------------------------------------------------
    # Tir / Mordad
    # --------------------------------------------------------

    elif jalali_month in [4, 5]:

        if category == "glass_cleaner":
            multiplier *= 1.10

        elif category == "dishwashing_liquid":
            multiplier *= 1.08

    # --------------------------------------------------------
    # Mehr
    # --------------------------------------------------------

    elif jalali_month == 7:

        if category == "hand_wash":
            multiplier *= 1.10

        elif category == "dishwashing_liquid":
            multiplier *= 1.05

    # --------------------------------------------------------
    # Dey
    # --------------------------------------------------------

    elif jalali_month == 10:

        if category == "hand_wash":
            multiplier *= 1.05

    return multiplier


# ============================================================
# WEEKLY SEASONALITY
# ============================================================

def get_day_multiplier(d):
    """
    Weekly purchasing behavior.

    Thursday:
        Slightly higher.

    Friday:
        Lower commercial activity.
    """

    # Python:
    # Monday = 0
    # Tuesday = 1
    # Wednesday = 2
    # Thursday = 3
    # Friday = 4

    if d.weekday() == 4:
        return 0.75

    if d.weekday() == 3:
        return 1.10

    return 1.0


# ============================================================
# DISTRIBUTION QUANTITY
# ============================================================

def get_distribution_quantity_multiplier(distribution_id):
    """
    Different distribution regions have
    different market sizes.
    """

    multipliers = {
        "D001": 1.80,
        "D002": 1.20,
        "D003": 1.50,
        "D004": 1.10,
        "D005": 1.10,
        "D006": 1.30,
        "D007": 1.00,
        "D008": 0.80,
        "D009": 0.90,
        "D010": 0.80,
        "D011": 0.80,
        "D012": 0.70,
        "D013": 0.80,
        "D014": 0.70,
        "D015": 0.70,

        "D016": 0.75,
        "D017": 0.75,
        "D018": 0.75,
        "D019": 0.70,
        "D020": 0.70,
        "D021": 0.70,
        "D022": 0.70,
        "D023": 0.65,
        "D024": 0.65,
        "D025": 0.65,
        "D026": 0.65,
        "D027": 0.60,
        "D028": 0.60,
        "D029": 0.60,
        "D030": 0.60,
        "D031": 0.55,
        "D032": 0.55,
        "D033": 0.55,
        "D034": 0.55,
        "D035": 0.50,
        "D036": 0.50,
    }

    return multipliers.get(
        distribution_id,
        1.0
    )


def generate_quantity(distribution_id):
    """
    Generate realistic sales quantity
    based on market size.
    """

    multiplier = get_distribution_quantity_multiplier(
        distribution_id
    )

    base_quantity = random.randint(
        5,
        80
    )

    quantity = round(
        base_quantity * multiplier
    )

    return max(
        1,
        quantity
    )


# ============================================================
# DISCOUNT
# ============================================================

def generate_discount(
    distribution_id,
    quantity
):
    """
    Larger orders generally receive
    larger discounts.
    """

    if quantity >= 150:

        return random.choice([
            7,
            8,
            10,
            12
        ])

    elif quantity >= 80:

        return random.choice([
            5,
            6,
            7,
            8
        ])

    elif quantity >= 40:

        return random.choice([
            3,
            4,
            5,
            6
        ])

    else:

        return random.choice([
            0,
            0,
            2,
            3
        ])


# ============================================================
# LOAD PRODUCTS
# ============================================================

products = []

with open(
    PRODUCTS_FILE,
    "r",
    encoding="utf-8-sig",
    newline=""
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        product_id = row["product_id"].strip()

        # Only use P001 through P020
        if product_id not in VALID_PRODUCT_IDS:
            continue

        # Make sure the product has a defined weight
        if product_id not in PRODUCT_WEIGHTS:
            continue

        row["product_id"] = product_id

        row["unit_price_rial"] = int(
            row["unit_price_rial"]
        )

        products.append(row)


# ============================================================
# LOAD DISTRIBUTORS
# ============================================================

distributors = []

with open(
    DISTRIBUTORS_FILE,
    "r",
    encoding="utf-8-sig",
    newline=""
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        distribution_id = row[
            "distribution_id"
        ].strip()

        # Only use D001 through D036
        if distribution_id not in VALID_DISTRIBUTION_IDS:
            continue

        # Make sure the distribution has a defined weight
        if distribution_id not in REGION_WEIGHTS:
            continue

        row["distribution_id"] = distribution_id

        distributors.append(row)


# ============================================================
# VALIDATION
# ============================================================

if not products:
    raise ValueError(
        "No valid products P001-P020 were found "
        "in products.csv."
    )

if not distributors:
    raise ValueError(
        "No valid distributions D001-D036 were found "
        "in distributions.csv."
    )


# ============================================================
# CREATE WEIGHTED LISTS
# ============================================================

product_weights = [
    PRODUCT_WEIGHTS[product["product_id"]]
    for product in products
]


region_weights = [
    REGION_WEIGHTS[distributor["distribution_id"]]
    for distributor in distributors
]


# ============================================================
# GENERATE DATE WEIGHTS
# ============================================================

all_dates = list(
    daterange(
        START_DATE,
        END_DATE
    )
)

date_weights = []

for d in all_dates:

    weight = get_day_multiplier(d)

    _, jalali_month, _ = gregorian_to_jalali(
        d.year,
        d.month,
        d.day
    )

    # General seasonal demand

    if jalali_month == 12:
        weight *= 1.30

    elif jalali_month == 1:
        weight *= 0.85

    elif jalali_month in [10, 11]:
        weight *= 1.05

    date_weights.append(weight)


# ============================================================
# GENERATE SALES
# ============================================================

sales = []

for sale_number in range(
    1,
    NUM_SALES + 1
):

    # --------------------------------------------------------
    # SELECT DATE
    # --------------------------------------------------------

    sale_date = random.choices(
        all_dates,
        weights=date_weights,
        k=1
    )[0]

    _, jalali_month, _ = gregorian_to_jalali(
        sale_date.year,
        sale_date.month,
        sale_date.day
    )

    # --------------------------------------------------------
    # SELECT PRODUCT
    # --------------------------------------------------------

    product = random.choices(
        products,
        weights=product_weights,
        k=1
    )[0]

    category = product["category"]

    # --------------------------------------------------------
    # CATEGORY SEASONALITY
    # --------------------------------------------------------

    seasonal_multiplier = (
        get_category_seasonality(
            category,
            jalali_month
        )
    )

    # 15% of transactions don't follow
    # the exact seasonal pattern.

    if random.random() < 0.15:
        seasonal_multiplier = 1.0

    # --------------------------------------------------------
    # SELECT DISTRIBUTION
    # --------------------------------------------------------

    distributor = random.choices(
        distributors,
        weights=region_weights,
        k=1
    )[0]

    distribution_id = distributor[
        "distribution_id"
    ]

    # --------------------------------------------------------
    # QUANTITY
    # --------------------------------------------------------

    quantity = generate_quantity(
        distribution_id
    )

    # Apply seasonal demand.

    if random.random() < 0.70:

        quantity = max(
            1,
            round(
                quantity
                * seasonal_multiplier
            )
        )

    # Natural variation.

    quantity = max(
        1,
        round(
            quantity
            * random.uniform(
                0.85,
                1.20
            )
        )
    )

    # --------------------------------------------------------
    # PRICE
    # --------------------------------------------------------

    base_price = product[
        "unit_price_rial"
    ]

    # Use the exact unit price from products.csv.
    # No variation is applied here.

    unit_price = base_price

    # --------------------------------------------------------
    # DISCOUNT
    # --------------------------------------------------------

    discount_percent = generate_discount(
        distribution_id,
        quantity
    )

    # --------------------------------------------------------
    # TOTAL PRICE
    # --------------------------------------------------------

    gross_price = (
        quantity
        * unit_price
    )

    total_price = round(
        gross_price
        * (
            1
            - discount_percent / 100
        )
    )

    # --------------------------------------------------------
    # CREATE SALE
    # --------------------------------------------------------

    sale = {
        "sale_id": sale_number,
        "date": sale_date.isoformat(),
        "product_id": product["product_id"],
        "distribution_id": distribution_id,
        "quantity": quantity,
        "unit_price_rial": unit_price,
        "discount_percent": discount_percent,
        "total_price_rial": total_price,
    }

    sales.append(sale)


# ============================================================
# ADD CONTROLLED DIRTY DATA
# ============================================================

# Approximately 2.5% of records will contain
# a controlled data-quality problem.

num_dirty = round(
    NUM_SALES * 0.025
)

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

    # --------------------------------------------------------
    # Missing Distribution ID
    # --------------------------------------------------------

    if error_type == "missing_region":

        row["distribution_id"] = ""

    # --------------------------------------------------------
    # Invalid Product ID
    # --------------------------------------------------------

    elif error_type == "invalid_product":

        row["product_id"] = "P999"

    # --------------------------------------------------------
    # Negative Quantity
    # --------------------------------------------------------

    elif error_type == "negative_quantity":

        row["quantity"] = -random.randint(
            1,
            10
        )

    # --------------------------------------------------------
    # Invalid Discount
    # --------------------------------------------------------

    elif error_type == "invalid_discount":

        row["discount_percent"] = random.choice([
            50,
            75,
            100,
            110
        ])

    # --------------------------------------------------------
    # Different Date Format
    # --------------------------------------------------------

    elif error_type == "date_format":

        row["date"] = row["date"].replace(
            "-",
            "/"
        )

    # --------------------------------------------------------
    # Extra Spaces
    # --------------------------------------------------------

    elif error_type == "extra_spaces":

        row["product_id"] = (
            f' {row["product_id"]} '
        )

    # --------------------------------------------------------
    # Duplicate
    # --------------------------------------------------------

    elif error_type == "duplicate":

        if index > 0:

            previous = sales[index - 1]

            row.update(previous)

    # --------------------------------------------------------
    # Missing Price
    # --------------------------------------------------------

    elif error_type == "missing_price":

        row["unit_price_rial"] = ""

    # --------------------------------------------------------
    # Comma-formatted number
    # --------------------------------------------------------

    elif error_type == "comma_number":

        row["total_price_rial"] = (
            f'{row["total_price_rial"]:,}'
        )


# ============================================================
# WRITE CSV
# ============================================================

fieldnames = [
    "sale_id",
    "date",
    "product_id",
    "distribution_id",
    "quantity",
    "unit_price_rial",
    "discount_percent",
    "total_price_rial",
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


# ============================================================
# RESULT
# ============================================================

print(
    f"Generated {len(sales):,} sales records."
)

print(
    f"Valid products: P001-P020"
)

print(
    f"Valid distributions: D001-D036"
)

print(
    f"Output: {OUTPUT_FILE}"
)