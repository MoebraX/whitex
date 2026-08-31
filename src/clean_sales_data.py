from pathlib import Path
import datetime
import re

import pandas as pd
import numpy as np
import jdatetime


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

SALES_FILE = BASE_DIR / "data" / "sales.csv"
LOGS_FILE = BASE_DIR / "data" / "data_cleaning_logs.csv"
PRODUCTS_FILE = BASE_DIR / "data" / "products.csv"
DISTRIBUTIONS_FILE = BASE_DIR / "data" / "distributions.csv"

CLEAN_SALES_FILE = BASE_DIR / "data" / "clean_sales.csv"


# ============================================================
# FLAGS
# ============================================================

# VALID
# MISSING
# CALCULATED
# IMPUTED
# TYPE_FIXED
# INVALID
# OUTLIER
# INCONSISTENT
# UNKNOWN
# DUPLICATE
# VALIDATED
# REPAIRED


# ============================================================
# LOGGING
# ============================================================

def add_log(logs, sale_id, field, before, after, flag):

    logs.loc[len(logs)] = {
        "sale_id": sale_id,
        "date": datetime.datetime.now(),
        "modified_field": field,
        "before": before,
        "after": after,
        "flag": flag
    }


# ============================================================
# MISSING VALUE CHECK
# ============================================================

def is_missing(value):

    if value is None:
        return True

    try:
        if pd.isna(value):
            return True
    except (TypeError, ValueError):
        pass

    if isinstance(value, str) and value.strip() == "":
        return True

    return False


# ============================================================
# SALE ID
# ============================================================

def check_sale_id(clean_sales, row, logs):

    original = row["sale_id"]

    # --------------------------------------------------------
    # Missing
    # --------------------------------------------------------

    if is_missing(original):

        add_log(
            logs,
            row["sale_id"],
            "sale_id",
            original,
            "",
            "UNKNOWN"
        )

        return ""


    # --------------------------------------------------------
    # Convert to string
    # --------------------------------------------------------

    output = str(original).strip()


    # --------------------------------------------------------
    # Remove spaces
    # --------------------------------------------------------

    cleaned = output.replace(" ", "")

    if cleaned != output:

        add_log(
            logs,
            row["sale_id"],
            "sale_id",
            output,
            cleaned,
            "TYPE_FIXED"
        )

        output = cleaned


    if output == "":

        add_log(
            logs,
            row["sale_id"],
            "sale_id",
            original,
            "",
            "UNKNOWN"
        )

        return ""


    # --------------------------------------------------------
    # If clean_sales is empty, no duplicate is possible
    # --------------------------------------------------------

    if clean_sales.empty:

        return output


    # --------------------------------------------------------
    # Find same sale_id
    # --------------------------------------------------------

    similars = clean_sales[
        clean_sales["sale_id"].astype(str) == output
    ]


    if similars.empty:

        return output


    # --------------------------------------------------------
    # Compare all other fields
    # --------------------------------------------------------

    columns_to_compare = [
        "date",
        "product_id",
        "distribution_id",
        "quantity",
        "unit_price_rial",
        "discount_percent",
        "total_price_rial"
    ]


    for _, existing_row in similars.iterrows():

        same = True

        for column in columns_to_compare:

            a = existing_row[column]
            b = row[column]

            if is_missing(a) and is_missing(b):
                continue

            if str(a).strip() != str(b).strip():

                same = False
                break


        # ----------------------------------------------------
        # Exact duplicate
        #
        # Keep it. Do NOT remove it.
        # ----------------------------------------------------

        if same:

            add_log(
                logs,
                row["sale_id"],
                "sale_id",
                output,
                output,
                "DUPLICATE"
            )

            return output


    # --------------------------------------------------------
    # Same ID but different data
    #
    # Generate new integer ID
    # --------------------------------------------------------

    numeric_ids = pd.to_numeric(
        clean_sales["sale_id"],
        errors="coerce"
    ).dropna()


    if numeric_ids.empty:

        new_id = 1

    else:

        new_id = int(numeric_ids.max()) + 1


    add_log(
        logs,
        row["sale_id"],
        "sale_id",
        output,
        str(new_id),
        "TYPE_FIXED"
    )


    return str(new_id)


# ============================================================
# DATE PARSER
# ============================================================

def parse_date(value):

    if is_missing(value):
        return None, False

    value = str(value).strip()

    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y"
    ]

    for fmt in formats:

        try:

            # ------------------------------------------------
            # Detect Gregorian year
            # ------------------------------------------------

            year = int(value[:4])

            if 1900 <= year <= 2100:

                gregorian_date = datetime.datetime.strptime(
                    value,
                    fmt
                ).date()

                jalali_date = jdatetime.date.fromgregorian(
                    date=gregorian_date
                )

                return jalali_date, True

            # ------------------------------------------------
            # Treat as Jalali
            # ------------------------------------------------

            jalali_date = jdatetime.datetime.strptime(
                value,
                fmt
            ).date()

            return jalali_date, False

        except (ValueError, TypeError):
            continue

    return None, False


# ============================================================
# CHECK DATE
# ============================================================

def check_date(row, logs):

    original = row["date"]

    # --------------------------------------------------------
    # Missing
    # --------------------------------------------------------

    if is_missing(original):

        add_log(
            logs,
            row["sale_id"],
            "date",
            original,
            "",
            "UNKNOWN"
        )

        return ""


    output = str(original).strip()


    # --------------------------------------------------------
    # Remove spaces
    # --------------------------------------------------------

    cleaned = output.replace(" ", "")

    if cleaned != output:

        add_log(
            logs,
            row["sale_id"],
            "date",
            output,
            cleaned,
            "TYPE_FIXED"
        )

        output = cleaned


    # --------------------------------------------------------
    # Parse date
    # --------------------------------------------------------

    jdate, was_gregorian = parse_date(output)


    # --------------------------------------------------------
    # Invalid date
    # --------------------------------------------------------

    if jdate is None:

        add_log(
            logs,
            row["sale_id"],
            "date",
            output,
            "",
            "INVALID"
        )

        return ""


    # --------------------------------------------------------
    # Normalize to YYYY-MM-DD
    # --------------------------------------------------------

    normalized = jdate.strftime("%Y-%m-%d")


    # --------------------------------------------------------
    # Gregorian → Jalali
    # --------------------------------------------------------

    if was_gregorian:

        add_log(
            logs,
            row["sale_id"],
            "date",
            output,
            normalized,
            "TYPE_FIXED"
        )

    # --------------------------------------------------------
    # Jalali format normalization
    # --------------------------------------------------------

    elif normalized != output:

        add_log(
            logs,
            row["sale_id"],
            "date",
            output,
            normalized,
            "TYPE_FIXED"
        )


    output = normalized


    # --------------------------------------------------------
    # Date range validation
    # --------------------------------------------------------

    now = jdatetime.date.today()

    starting_date = jdatetime.date(
        1345,
        1,
        1
    )


    if jdate > now or jdate < starting_date:

        add_log(
            logs,
            row["sale_id"],
            "date",
            output,
            output,
            "INVALID"
        )


    # --------------------------------------------------------
    # One-year outlier
    # --------------------------------------------------------

    difference_days = (
        now.toordinal()
        - jdate.toordinal()
    )


    if abs(difference_days) > 365:

        add_log(
            logs,
            row["sale_id"],
            "date",
            output,
            output,
            "OUTLIER"
        )


    return output
# ============================================================
# PRODUCT ID
# ============================================================

def check_product_id(row, products, logs):

    original = row["product_id"]


    if is_missing(original):

        add_log(
            logs,
            row["sale_id"],
            "product_id",
            original,
            "",
            "UNKNOWN"
        )

        return ""


    output = str(original).strip()

    cleaned = output.replace(" ", "")


    if cleaned != output:

        add_log(
            logs,
            row["sale_id"],
            "product_id",
            output,
            cleaned,
            "TYPE_FIXED"
        )

        output = cleaned


    valid_products = (
        products["product_id"]
        .astype(str)
        .str.strip()
    )


    if output not in valid_products.values:

        add_log(
            logs,
            row["sale_id"],
            "product_id",
            output,
            output,
            "INVALID"
        )


    return output


# ============================================================
# DISTRIBUTION ID
# ============================================================

def check_distribution_id(row, distributions, logs):

    original = row["distribution_id"]


    if is_missing(original):

        add_log(
            logs,
            row["sale_id"],
            "distribution_id",
            original,
            "",
            "UNKNOWN"
        )

        return ""


    output = str(original).strip()

    cleaned = (
        output
        .replace(" ", "")
        .upper()
    )


    if cleaned != output:

        add_log(
            logs,
            row["sale_id"],
            "distribution_id",
            output,
            cleaned,
            "TYPE_FIXED"
        )

        output = cleaned


    valid_distributions = (
        distributions["distribution_id"]
        .astype(str)
        .str.strip()
        .str.replace(" ", "", regex=False)
        .str.upper()
    )


    if output not in valid_distributions.values:

        add_log(
            logs,
            row["sale_id"],
            "distribution_id",
            output,
            output,
            "INVALID"
        )


    return output


# ============================================================
# INTEGER CLEANER
# ============================================================

def check_isint(input, column_name, logs):

    output = input


    # --------------------------------------------------------
    # Missing
    # --------------------------------------------------------

    if is_missing(output):

        add_log(
            logs,
            row["sale_id"],
            column_name,
            input,
            "",
            "MISSING"
        )

        return False


    # --------------------------------------------------------
    # Integer
    # --------------------------------------------------------

    if isinstance(output, (int, np.integer)):

        return str(int(output))


    # --------------------------------------------------------
    # Float
    #
    # 123.98 -> 123
    # -123.98 -> -123
    # --------------------------------------------------------

    if isinstance(output, (float, np.floating)):

        if np.isnan(output):

            add_log(
                logs,
                row["sale_id"],
                column_name,
                input,
                "",
                "MISSING"
            )

            return False


        new_output = str(int(output))


        if new_output != str(output):

            add_log(
                logs,
                row["sale_id"],
                column_name,
                input,
                new_output,
                "TYPE_FIXED"
            )


        return new_output


    # --------------------------------------------------------
    # String
    # --------------------------------------------------------

    if isinstance(output, str):

        original = output.strip()


        if original == "":

            add_log(
                logs,
                row["sale_id"],
                column_name,
                input,
                "",
                "MISSING"
            )

            return False


        # ----------------------------------------------------
        # Remove spaces
        # ----------------------------------------------------

        cleaned = original.replace(" ", "")


        # ----------------------------------------------------
        # Detect negative number BEFORE removing characters
        #
        # Examples:
        # -123
        # -123.98
        # abc-123
        # ----------------------------------------------------

        negative = "-" in cleaned


        # ----------------------------------------------------
        # Remove commas used as thousands separators
        #
        # 12,345.67 -> 12345.67
        # ----------------------------------------------------

        cleaned = cleaned.replace(",", "")


        # ----------------------------------------------------
        # Find decimal number
        #
        # 123.98      -> 123
        # abc123.98   -> 123
        # 12,345.67   -> 12345
        # ----------------------------------------------------

        decimal_match = re.search(
            r"\d+\.\d+",
            cleaned
        )


        if decimal_match:

            number = decimal_match.group()

            integer_part = str(
                int(float(number))
            )


            if negative:

                integer_part = "-" + integer_part


            output = integer_part


        else:

            # ------------------------------------------------
            # Extract digits
            # ------------------------------------------------

            digits = re.sub(
                r"[^0-9]",
                "",
                cleaned
            )


            if digits == "":

                add_log(
                    logs,
                    row["sale_id"],
                    column_name,
                    input,
                    "",
                    "MISSING"
                )

                return False


            output = str(int(digits))


            if negative:

                output = "-" + output


        # ----------------------------------------------------
        # Log modification
        # ----------------------------------------------------

        if output != original:

            add_log(
                logs,
                row["sale_id"],
                column_name,
                input,
                output,
                "TYPE_FIXED"
            )


        return output


    # --------------------------------------------------------
    # Other numeric/object values
    # --------------------------------------------------------

    try:

        output = str(int(output))


        add_log(
            logs,
            row["sale_id"],
            column_name,
            input,
            output,
            "TYPE_FIXED"
        )


        return output


    except (ValueError, TypeError):

        add_log(
            logs,
            row["sale_id"],
            column_name,
            input,
            "",
            "MISSING"
        )

        return False


# ============================================================
# INVALID QUDT VALUES
# ============================================================

def invalidate_qudt_values(
    quantity,
    unit_price,
    discount,
    total_price,
    logs
):

    values = [
        ("quantity", quantity),
        ("unit_price_rial", unit_price),
        ("discount_percent", discount),
        ("total_price_rial", total_price)
    ]


    for field, value in values:

        if value is False or value is None:
            continue


        # ----------------------------------------------------
        # Negative values are invalid
        # ----------------------------------------------------

        if value < 0:

            add_log(
                logs,
                row["sale_id"],
                field,
                value,
                "",
                "INVALID"
            )


            if field == "quantity":
                quantity = False

            elif field == "unit_price_rial":
                unit_price = False

            elif field == "discount_percent":
                discount = False

            elif field == "total_price_rial":
                total_price = False


    # --------------------------------------------------------
    # Discount must be between 0 and 100
    # --------------------------------------------------------

    if (
        discount is not False
        and discount is not None
        and not 0 <= discount <= 100
    ):

        add_log(
            logs,
            row["sale_id"],
            "discount_percent",
            discount,
            "",
            "INVALID"
        )

        discount = False


    return (
        quantity,
        unit_price,
        discount,
        total_price
    )


# ============================================================
# QUDT
# ============================================================

def check_QUDT(row, sales_df, logs_df):

    # --------------------------------------------------------
    # 1. Clean values
    # --------------------------------------------------------

    quantity = check_isint(
        row["quantity"],
        "quantity",
        logs_df
    )

    unit_price = check_isint(
        row["unit_price_rial"],
        "unit_price_rial",
        logs_df
    )

    discount = check_isint(
        row["discount_percent"],
        "discount_percent",
        logs_df
    )

    total_price = check_isint(
        row["total_price_rial"],
        "total_price_rial",
        logs_df
    )


    # --------------------------------------------------------
    # Convert to integers
    # --------------------------------------------------------

    quantity = (
        int(quantity)
        if quantity is not False
        else False
    )

    unit_price = (
        int(unit_price)
        if unit_price is not False
        else False
    )

    discount = (
        int(discount)
        if discount is not False
        else False
    )

    total_price = (
        int(total_price)
        if total_price is not False
        else False
    )


    # --------------------------------------------------------
    # IMPORTANT:
    # Negative / invalid values become missing here.
    # They then continue through the repair pipeline.
    # --------------------------------------------------------

    (
        quantity,
        unit_price,
        discount,
        total_price
    ) = invalidate_qudt_values(
        quantity,
        unit_price,
        discount,
        total_price,
        logs_df
    )


    # --------------------------------------------------------
    # Calculation helpers
    # --------------------------------------------------------

    def calculate_total(q, p, d):

        if (
            q is False
            or p is False
            or d is False
        ):
            return None

        return round(
            q * p * (1 - d / 100)
        )


    def calculate_unit_price(q, total, d):

        if (
            q is False
            or q is None
            or q == 0
        ):
            return None

        if (
            total is False
            or d is False
        ):
            return None


        divisor = q * (1 - d / 100)


        if divisor == 0:
            return None


        return round(
            total / divisor
        )


    def calculate_quantity(total, p, d):

        if (
            total is False
            or p is False
            or p is None
            or p == 0
        ):
            return None

        if d is False:
            return None


        divisor = p * (1 - d / 100)


        if divisor == 0:
            return None


        return round(
            total / divisor
        )


    def calculate_discount(q, p, total):

        if (
            q is False
            or q is None
            or q == 0
        ):
            return None

        if (
            p is False
            or p is None
            or p == 0
        ):
            return None

        if total is False:
            return None


        discount = (
            1 -
            total / (q * p)
        ) * 100


        discount = round(discount)


        # Calculated discount must also be valid

        if not 0 <= discount <= 100:
            return None


        return discount


    # --------------------------------------------------------
    # Helper for checking if all values exist
    # --------------------------------------------------------

    def get_values():

        return [
            quantity,
            unit_price,
            discount,
            total_price
        ]


    # --------------------------------------------------------
    # 2. All values exist
    # --------------------------------------------------------

    values = get_values()


    if all(
        value is not False and value is not None
        for value in values
    ):

        return values


    # --------------------------------------------------------
    # 3. One missing value
    # --------------------------------------------------------

    missing_count = sum(
        value is False or value is None
        for value in values
    )


    if missing_count == 1:

        if quantity is False or quantity is None:

            quantity = calculate_quantity(
                total_price,
                unit_price,
                discount
            )

            if quantity is not None:

                add_log(
                    logs_df,
                    row["sale_id"],
                    "quantity",
                    "",
                    quantity,
                    "CALCULATED"
                )


        elif unit_price is False or unit_price is None:

            unit_price = calculate_unit_price(
                quantity,
                total_price,
                discount
            )

            if unit_price is not None:

                add_log(
                    logs_df,
                    row["sale_id"],
                    "unit_price_rial",
                    "",
                    unit_price,
                    "CALCULATED"
                )


        elif discount is False or discount is None:

            discount = calculate_discount(
                quantity,
                unit_price,
                total_price
            )

            if discount is not None:

                add_log(
                    logs_df,
                    row["sale_id"],
                    "discount_percent",
                    "",
                    discount,
                    "CALCULATED"
                )


        elif total_price is False or total_price is None:

            total_price = calculate_total(
                quantity,
                unit_price,
                discount
            )

            if total_price is not None:

                add_log(
                    logs_df,
                    row["sale_id"],
                    "total_price_rial",
                    "",
                    total_price,
                    "CALCULATED"
                )


        # ----------------------------------------------------
        # IMPORTANT:
        # Validate ALL four fields before returning.
        # ----------------------------------------------------

        values = get_values()


        if any(
            value is False or value is None
            for value in values
        ):

            # Don't return prematurely.
            # Continue to reference-data recovery below.

            pass

        else:

            return values


    # ========================================================
    # 4. REFERENCE DATA
    # ========================================================

    product_id = str(
        row["product_id"]
    ).strip()


    reference_df = sales_df[
        sales_df["product_id"]
        .astype(str)
        .str.strip()
        == product_id
    ].copy()


    # --------------------------------------------------------
    # Convert reference numeric columns once
    # --------------------------------------------------------

    if not reference_df.empty:

        reference_df["_quantity"] = pd.to_numeric(
            reference_df["quantity"],
            errors="coerce"
        )

        reference_df["_unit_price"] = pd.to_numeric(
            reference_df["unit_price_rial"],
            errors="coerce"
        )

        reference_df["_discount"] = pd.to_numeric(
            reference_df["discount_percent"],
            errors="coerce"
        )

        reference_df["_total_price"] = pd.to_numeric(
            reference_df["total_price_rial"],
            errors="coerce"
        )


    # ========================================================
    # 5. RECOVER UNIT PRICE
    # ========================================================

    if (
        unit_price is False
        and not reference_df.empty
    ):

        nearby = reference_df


        current_date = parse_jalali_date(
            row["date"]
        )


        if current_date is not None:

            reference_df["_jdate"] = (
                reference_df["date"]
                .apply(parse_jalali_date)
            )


            reference_df["_date_distance"] = (
                reference_df["_jdate"]
                .apply(
                    lambda d:
                    abs(
                        d.toordinal()
                        - current_date.toordinal()
                    )
                    if d is not None
                    else None
                )
            )


            nearby = reference_df[
                reference_df["_date_distance"].notna()
                &
                (
                    reference_df["_date_distance"]
                    <= 30
                )
            ]


        prices = nearby["_unit_price"].dropna()


        if not prices.empty:

            unit_price = round(
                prices.median()
            )


            add_log(
                logs_df,
                row["sale_id"],
                "unit_price_rial",
                "",
                unit_price,
                "IMPUTED"
            )

        else:

            add_log(
                logs_df,
                row["sale_id"],
                "unit_price_rial",
                "",
                "",
                "UNKNOWN"
            )


    # ========================================================
    # 6. RECOVER DISCOUNT
    # ========================================================

    if (
        discount is False
        and not reference_df.empty
    ):

        # ----------------------------------------------------
        # Similar quantity
        # ----------------------------------------------------

        if quantity is not False:

            similar = reference_df[
                reference_df["_quantity"].notna()
                &
                (
                    reference_df["_quantity"]
                    >= quantity * 0.8
                )
                &
                (
                    reference_df["_quantity"]
                    <= quantity * 1.2
                )
            ]


            discounts = (
                similar["_discount"]
                .dropna()
            )


            if not discounts.empty:

                discount = round(
                    discounts.median()
                )


                add_log(
                    logs_df,
                    row["sale_id"],
                    "discount_percent",
                    "",
                    discount,
                    "IMPUTED"
                )


        # ----------------------------------------------------
        # If quantity is unavailable,
        # use similar total price
        # ----------------------------------------------------

        if (
            discount is False
            and total_price is not False
        ):

            similar = reference_df[
                reference_df["_total_price"].notna()
                &
                (
                    reference_df["_total_price"]
                    >= total_price * 0.8
                )
                &
                (
                    reference_df["_total_price"]
                    <= total_price * 1.2
                )
            ]


            discounts = (
                similar["_discount"]
                .dropna()
            )


            if not discounts.empty:

                discount = round(
                    discounts.median()
                )


                add_log(
                    logs_df,
                    row["sale_id"],
                    "discount_percent",
                    "",
                    discount,
                    "IMPUTED"
                )


        if discount is False:

            add_log(
                logs_df,
                row["sale_id"],
                "discount_percent",
                "",
                "",
                "UNKNOWN"
            )


    # ========================================================
    # 7. Recalculate if only one remains missing
    # ========================================================

    values = get_values()


    missing_count = sum(
        value is False or value is None
        for value in values
    )


    if missing_count == 1:

        if quantity is False or quantity is None:

            quantity = calculate_quantity(
                total_price,
                unit_price,
                discount
            )


            if quantity is not None:

                add_log(
                    logs_df,
                    row["sale_id"],
                    "quantity",
                    "",
                    quantity,
                    "CALCULATED"
                )


        elif unit_price is False or unit_price is None:

            unit_price = calculate_unit_price(
                quantity,
                total_price,
                discount
            )


            if unit_price is not None:

                add_log(
                    logs_df,
                    row["sale_id"],
                    "unit_price_rial",
                    "",
                    unit_price,
                    "CALCULATED"
                )


        elif discount is False or discount is None:

            discount = calculate_discount(
                quantity,
                unit_price,
                total_price
            )


            if discount is not None:

                add_log(
                    logs_df,
                    row["sale_id"],
                    "discount_percent",
                    "",
                    discount,
                    "CALCULATED"
                )


        elif total_price is False or total_price is None:

            total_price = calculate_total(
                quantity,
                unit_price,
                discount
            )


            if total_price is not None:

                add_log(
                    logs_df,
                    row["sale_id"],
                    "total_price_rial",
                    "",
                    total_price,
                    "CALCULATED"
                )


    # ========================================================
    # 8. RECOVER QUANTITY
    # ========================================================

    if (
        quantity is False
        and not reference_df.empty
    ):

        similar = reference_df.copy()


        # ----------------------------------------------------
        # Similar total price
        # ----------------------------------------------------

        if total_price is not False:

            similar = similar[
                similar["_total_price"].notna()
                &
                (
                    similar["_total_price"]
                    >= total_price * 0.8
                )
                &
                (
                    similar["_total_price"]
                    <= total_price * 1.2
                )
            ]


        # ----------------------------------------------------
        # Similar discount
        # ----------------------------------------------------

        if discount is not False:

            similar = similar[
                similar["_discount"].notna()
                &
                (
                    similar["_discount"]
                    == discount
                )
            ]


        quantities = (
            similar["_quantity"]
            .dropna()
        )


        if not quantities.empty:

            quantity = round(
                quantities.median()
            )


            add_log(
                logs_df,
                row["sale_id"],
                "quantity",
                "",
                quantity,
                "IMPUTED"
            )


        else:

            # ------------------------------------------------
            # Fallback:
            # all same-product quantities
            # ------------------------------------------------

            quantities = (
                reference_df["_quantity"]
                .dropna()
            )


            if not quantities.empty:

                quantity = round(
                    quantities.median()
                )


                add_log(
                    logs_df,
                    row["sale_id"],
                    "quantity",
                    "",
                    quantity,
                    "IMPUTED"
                )


    # ========================================================
    # 9. RECOVER TOTAL PRICE
    # ========================================================

    if (
        total_price is False
        and not reference_df.empty
    ):

        similar = reference_df.copy()


        # ----------------------------------------------------
        # Similar quantity
        # ----------------------------------------------------

        if quantity is not False:

            similar = similar[
                similar["_quantity"].notna()
                &
                (
                    similar["_quantity"]
                    >= quantity * 0.8
                )
                &
                (
                    similar["_quantity"]
                    <= quantity * 1.2
                )
            ]


        totals = (
            similar["_total_price"]
            .dropna()
        )


        if not totals.empty:

            total_price = round(
                totals.median()
            )


            add_log(
                logs_df,
                row["sale_id"],
                "total_price_rial",
                "",
                total_price,
                "IMPUTED"
            )


    # ========================================================
    # 10. FINAL CALCULATION
    # ========================================================

    values = get_values()


    missing_count = sum(
        value is False or value is None
        for value in values
    )


    if missing_count == 1:

        if quantity is False or quantity is None:

            quantity = calculate_quantity(
                total_price,
                unit_price,
                discount
            )


            if quantity is not None:

                add_log(
                    logs_df,
                    row["sale_id"],
                    "quantity",
                    "",
                    quantity,
                    "CALCULATED"
                )


        elif unit_price is False or unit_price is None:

            unit_price = calculate_unit_price(
                quantity,
                total_price,
                discount
            )


            if unit_price is not None:

                add_log(
                    logs_df,
                    row["sale_id"],
                    "unit_price_rial",
                    "",
                    unit_price,
                    "CALCULATED"
                )


        elif discount is False or discount is None:

            discount = calculate_discount(
                quantity,
                unit_price,
                total_price
            )


            if discount is not None:

                add_log(
                    logs_df,
                    row["sale_id"],
                    "discount_percent",
                    "",
                    discount,
                    "CALCULATED"
                )


        elif total_price is False or total_price is None:

            total_price = calculate_total(
                quantity,
                unit_price,
                discount
            )


            if total_price is not None:

                add_log(
                    logs_df,
                    row["sale_id"],
                    "total_price_rial",
                    "",
                    total_price,
                    "CALCULATED"
                )


    # ========================================================
    # 11. FINAL VALIDATION
    # ========================================================

    values = [
        quantity,
        unit_price,
        discount,
        total_price
    ]


    # Quantity and total price are mandatory

    if (
        quantity is False
        or quantity is None
    ):

        return False


    if (
        total_price is False
        or total_price is None
    ):

        return False


    # Unit price and discount are also required
    # for a complete QUDT record

    if (
        unit_price is False
        or unit_price is None
    ):

        return False


    if (
        discount is False
        or discount is None
    ):

        return False


    # --------------------------------------------------------
    # Final validity checks
    # --------------------------------------------------------

    if quantity < 0:
        return False

    if unit_price < 0:
        return False

    if total_price < 0:
        return False

    if not 0 <= discount <= 100:
        return False


    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return [
        int(quantity),
        int(unit_price),
        int(discount),
        int(total_price)
    ]


# ============================================================
# CONSISTENCY CHECK
# ============================================================

def is_consistent(
    quantity,
    unit_price_rial,
    discount_percent,
    total_price_rial,
    logs
):

    # --------------------------------------------------------
    # Safety validation
    # --------------------------------------------------------

    if any(
        value is None or value is False
        for value in [
            quantity,
            unit_price_rial,
            discount_percent,
            total_price_rial
        ]
    ):

        return False


    expected_total = round(
        quantity
        * unit_price_rial
        * (1 - discount_percent / 100)
    )


    # --------------------------------------------------------
    # Avoid division by zero
    # --------------------------------------------------------

    if expected_total == 0:

        consistent = (
            total_price_rial == 0
        )


        if not consistent:

            add_log(
                logs,
                row["sale_id"],
                "total_price_rial",
                total_price_rial,
                total_price_rial,
                "INCONSISTENT"
            )


        return consistent


    # --------------------------------------------------------
    # Difference percentage
    # --------------------------------------------------------

    difference_percent = (
        abs(
            total_price_rial
            - expected_total
        )
        / abs(expected_total)
        * 100
    )


    # --------------------------------------------------------
    # 5% tolerance
    # --------------------------------------------------------

    if difference_percent > 5:

        add_log(
            logs,
            row["sale_id"],
            "total_price_rial",
            total_price_rial,
            total_price_rial,
            "INCONSISTENT"
        )

        return False


    return True


# ============================================================
# LOAD DATA
# ============================================================

sales = pd.read_csv(
    SALES_FILE,
    dtype=str
)


products = pd.read_csv(
    PRODUCTS_FILE,
    dtype=str
)


distributions = pd.read_csv(
    DISTRIBUTIONS_FILE,
    dtype=str
)


logs = pd.read_csv(
    LOGS_FILE
)


# ============================================================
# PREPARE CLEAN DATAFRAME
# ============================================================

clean_sales = sales.iloc[0:0].copy()


# Make sure the output column exists

clean_sales["is_consistent"] = pd.Series(
    dtype=bool
)


# ============================================================
# PROCESS SALES
# ============================================================
counter = 1
for index, row in sales.iterrows():

    # --------------------------------------------------------
    # Sale ID
    # --------------------------------------------------------

    sale_id = check_sale_id(
        clean_sales,
        row,
        logs
    )


    # --------------------------------------------------------
    # IMPORTANT:
    # Duplicates are intentionally KEPT.
    #
    # check_sale_id returns the existing ID for exact
    # duplicates instead of False.
    # --------------------------------------------------------


    # --------------------------------------------------------
    # Date
    # --------------------------------------------------------

    thedate = check_date(
        row,
        logs
    )


    # --------------------------------------------------------
    # Product
    # --------------------------------------------------------

    product_id = check_product_id(
        row,
        products,
        logs
    )


    # --------------------------------------------------------
    # Distribution
    # --------------------------------------------------------

    distribution_id = check_distribution_id(
        row,
        distributions,
        logs
    )


    # --------------------------------------------------------
    # QUDT
    # --------------------------------------------------------

    # Pass the original row because the reference data
    # should come from the original sales dataset.

    results = check_QUDT(
        row,
        sales,
        logs
    )


    # --------------------------------------------------------
    # QUDT could not be recovered
    # --------------------------------------------------------

    if results is False:

        add_log(
            logs,
            row["sale_id"],
            "quantity/unit_price/discount/total_price",
            "",
            "",
            "UNKNOWN"
        )

        continue


    quantity = results[0]
    unit_price_rial = results[1]
    discount_percent = results[2]
    total_price_rial = results[3]


    # --------------------------------------------------------
    # Consistency
    # --------------------------------------------------------

    consistency = is_consistent(
        quantity,
        unit_price_rial,
        discount_percent,
        total_price_rial,
        logs
    )


    # --------------------------------------------------------
    # Add clean row
    # --------------------------------------------------------

    clean_sales.loc[len(clean_sales)] = {

        "sale_id": sale_id,

        "date": thedate,

        "product_id": product_id,

        "distribution_id": distribution_id,

        "quantity": quantity,

        "unit_price_rial": unit_price_rial,

        "discount_percent": discount_percent,

        "total_price_rial": total_price_rial,

        "is_consistent": consistency
    }

    print("Done: ",counter," out of 50000")
    counter=counter+1


# ============================================================
# SAVE CLEAN DATA
# ============================================================

clean_sales.to_csv(
    CLEAN_SALES_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# SAVE LOGS
# ============================================================

logs.to_csv(
    LOGS_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# SUMMARY
# ============================================================

print(
    f"Original rows: {len(sales):,}"
)

print(
    f"Clean rows: {len(clean_sales):,}"
)

print(
    f"Removed rows: "
    f"{len(sales) - len(clean_sales):,}"
)

print(
    f"Logs: {len(logs):,}"
)

print(
    f"Clean file: {CLEAN_SALES_FILE}"
)