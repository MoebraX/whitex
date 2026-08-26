import csv
from pathlib import Path
import pandas as pd
from datetime import date, timedelta, datetime
import jdatetime
import re

BASE_DIR = Path(__file__).resolve().parent.parent
SALES_FILE = BASE_DIR / "data" / "sales.csv"
LOGS_FILE = BASE_DIR / "data" / "data_cleaning_logs.csv"
PRODUCTS_FILE = BASE_DIR / "data" / "products.csv"
DISTRIBUTIONS_FILE = BASE_DIR / "data" / "distributions.csv"

#FLAGS: VALID, MISSING, CALCULATED, IMPUTED, TYPE_FIXED, INVALID, OUTLIER, INCONSISTENT, UNKNOWN, DUPLICATE, VALIDATED, REPAIRED

def check_sale_id(clean_sales, row, logs):
    output = row["sale_id"]
    if " " in output:
        logs.loc[len(logs)] = {
            "date": datetime.now(),
            "modified_field": "sale_id",
            "before": output,
            "after": output.replace(" ",""),
            "flag": "TYPE_FIXED"
        }
        output = output.replace(" ","")
    if output == "":
        logs.loc[len(logs)] = {
            "date": datetime.now(),
            "modified_field": "sale_id",
            "before": output,
            "after": output,
            "flag": "UNKNOWN"
        }
        return output

    similars=clean_sales[clean_sales["sale_id"] == output]
    if not similars.empty:
        columns_to_compare = [
            "date",
            "product_id",
            "distribution_id",
            "quantity",
            "unit_price_toman",
            "discount_percent",
            "total_price_toman"
        ]
        for _, existing_row in similars.iterrows():
            if existing_row[columns_to_compare].equals(
                row[columns_to_compare]
            ):
                logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": "sale_id",
                    "before": output,
                    "after": output,
                    "flag": "DUPLICATE"
                }
                break
    return output

def check_date(row, logs):
    output = row["date"]
    if " " in output:
        logs.loc[len(logs)] = {
            "date": datetime.now(),
            "modified_field": "date",
            "before": output,
            "after": output.replace(" ",""),
            "flag": "TYPE_FIXED"
        }
        output = output.replace(" ","")
    if output == "":
        logs.loc[len(logs)] = {
                "date": datetime.now(),
                "modified_field": "date",
                "before": output,
                "after": output,
                "flag": "UNKNOWN"
            }
        return output
    try:
        datetime.strptime(output, "%Y-%m-%d")
    except (ValueError, TypeError):
        new_output = ""
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
        ]
        for fmt in formats:
            try:
                date = datetime.strptime(output, fmt)
                new_output = date.strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                continue
        if new_output == "":
                logs.loc[len(logs)] = {
                "date": datetime.now(),
                "modified_field": "date",
                "before": output,
                "after": new_output,
                "flag": "INVALID"
            }
        else:
            logs.loc[len(logs)] = {
                "date": datetime.now(),
                "modified_field": "date",
                "before": output,
                "after": new_output,
                "flag": "TYPE_FIXED"
            }
        output = new_output
    jdate = jdatetime.datetime.strptime(output, "%Y-%m-%d").date()
    now = jdatetime.datetime.today()
    starting_date = jdatetime.date(1345,1,1)
    if jdate>now or jdate<starting_date:
        logs.loc[len(logs)] = {
                "date": datetime.now(),
                "modified_field": "date",
                "before": output,
                "after": output,
                "flag": "INVALID"
            }
    difference = output - datetime.now()
    if difference < timedelta(days=365):
        logs.loc[len(logs)] = {
                "date": datetime.now(),
                "modified_field": "date",
                "before": output,
                "after": output,
                "flag": "OUTLIER"
            }
    return output

def check_product_id(row, products, logs):
    output = row["product_id"]
    if " " in output:
        logs.loc[len(logs)] = {
            "date": datetime.now(),
            "modified_field": "product_id",
            "before": output,
            "after": output.replace(" ",""),
            "flag": "TYPE_FIXED"
        }
        output = output.replace(" ","")
    if output == "":
        logs.loc[len(logs)] = {
                "date": datetime.now(),
                "modified_field": "product_id",
                "before": output,
                "after": output,
                "flag": "UNKNOWN"
            }
        return output
    if not (products["product_id"] == output).any():
        logs.loc[len(logs)] = {
            "date": datetime.now(),
            "modified_field": "product_id",
            "before": output,
            "after": output,
            "flag": "INVALID"
        }
    return output
    
def check_distribution_id(row, distributions, logs):
    output = row["distribution_id"]
    if " " in output:
        logs.loc[len(logs)] = {
            "date": datetime.now(),
            "modified_field": "distribution_id",
            "before": output,
            "after": output.replace(" ",""),
            "flag": "TYPE_FIXED"
        }
        output = output.replace(" ","")
    if output == "":
        logs.loc[len(logs)] = {
                "date": datetime.now(),
                "modified_field": "distribution_id",
                "before": output,
                "after": output,
                "flag": "UNKNOWN"
            }
        return output
    if not (distributions["distribution_id"] == output).any():
        logs.loc[len(logs)] = {
            "date": datetime.now(),
            "modified_field": "distribution_id",
            "before": output,
            "after": output,
            "flag": "INVALID"
        }
    return output

def check_isint(input, column_name, logs):
    output=input
    if isinstance(output, int):
        return str(output)
    if isinstance(output, str):
        if " " in output:
            output = output.replace(" ","")
        output = re.sub(r"[^0-9]", "", output)
        if output == "":
            logs.loc[len(logs)] = {
                "date": datetime.now(),
                "modified_field": column_name,
                "before": input,
                "after": output,
                "flag": "MISSING"
            }
            return False
        else:
            try:
                output = int(output)
                logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": column_name,
                    "before": input,
                    "after": output,
                    "flag": "TYPE_FIXED"
                    }
                return str(output)
            except:
                logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": column_name,
                    "before": input,
                    "after": output,
                    "flag": "MISSING"
                    }
                return False
    else:
        try:
            output = int(output)
            logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": column_name,
                    "before": input,
                    "after": output,
                    "flag": "TYPE_FIXED"
                }
            return str(output)
        except:
            logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": column_name,
                    "before": input,
                    "after": output,
                    "flag": "MISSING"
                }
            return False

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def check_QUDT(row, sales_df, logs_df):

    # ============================================================
    # 1. CHECK THE FOUR VALUES
    # ============================================================

    quantity = check_isint(
        row["quantity"],
        "quantity",
        logs_df
    )

    unit_price = check_isint(
        row["unit_price_toman"],
        "unit_price_toman",
        logs_df
    )

    discount = check_isint(
        row["discount_percent"],
        "discount_percent",
        logs_df
    )

    total_price = check_isint(
        row["total_price_toman"],
        "total_price_toman",
        logs_df
    )

    # Convert existing values to integers
    if quantity is not False:
        quantity = int(quantity)

    if unit_price is not False:
        unit_price = int(unit_price)

    if discount is not False:
        discount = int(discount)

    if total_price is not False:
        total_price = int(total_price)


    # ============================================================
    # 2. IF EVERYTHING EXISTS, RETURN IT
    # ============================================================

    values = [
        quantity,
        unit_price,
        discount,
        total_price
    ]

    if all(value is not False for value in values):
        return values


    # ============================================================
    # HELPER: CALCULATE TOTAL PRICE
    # ============================================================

    def calculate_total(quantity, unit_price, discount):

        return round(
            quantity *
            unit_price *
            (1 - discount / 100)
        )


    # ============================================================
    # HELPER: CALCULATE UNIT PRICE
    # ============================================================

    def calculate_unit_price(quantity, total_price, discount):

        if quantity == 0:
            return None

        divisor = quantity * (1 - discount / 100)

        if divisor == 0:
            return None

        return round(total_price / divisor)

    # ============================================================
    # HELPER: Date handling
    # ============================================================
    def parse_jalali_date(date_string):
        try:
            return jdatetime.datetime.strptime(
                str(date_string).strip(),
                "%Y-%m-%d"
            ).date()
        except (ValueError, TypeError):
            return None
    # ============================================================
    # HELPER: CALCULATE QUANTITY
    # ============================================================

    def calculate_quantity(total_price, unit_price, discount):

        divisor = unit_price * (1 - discount / 100)

        if divisor == 0:
            return None

        return round(total_price / divisor)


    # ============================================================
    # 3. IF ONLY ONE VALUE IS MISSING
    # ============================================================

    missing_count = sum(
        value is False
        for value in values
    )

    if missing_count == 1:

        # Missing quantity
        if quantity is False:
            quantity = calculate_quantity(
                total_price,
                unit_price,
                discount
            )
            logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": "quantity",
                    "before": "",
                    "after": quantity,
                    "flag": "CALCULATED"
            }

        # Missing unit price
        elif unit_price is False:
            unit_price = calculate_unit_price(
                quantity,
                total_price,
                discount
            )
            logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": "unit_price_toman",
                    "before": "",
                    "after": unit_price,
                    "flag": "CALCULATED"
            }

        # Missing discount
        elif discount is False:

            if quantity * unit_price != 0:

                discount = round(
                    (1 - total_price / (quantity * unit_price))
                    * 100
                )
                logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": "discount_percent",
                    "before": "",
                    "after": discount,
                    "flag": "CALCULATED"
                }

        # Missing total price
        elif total_price is False:
            total_price = calculate_total(
                quantity,
                unit_price,
                discount
            )
            logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": "total_price_toman",
                    "before": "",
                    "after": total_price,
                    "flag": "CALCULATED"
            }

        values = [
            quantity,
            unit_price,
            discount,
            total_price
        ]

        # Quantity and total price are mandatory
        if quantity is False or quantity is None:
            return False

        if total_price is False or total_price is None:
            return False

        return values


    # ============================================================
    # 4. MULTIPLE VALUES ARE MISSING
    # ============================================================

    product_id = row["product_id"]

    # Make a copy so we don't modify the original dataframe
    reference_df = sales_df.copy()

    # Only use the same product
    reference_df = reference_df[
        reference_df["product_id"] == product_id
    ]


    # ============================================================
    # 5. RECOVER UNIT PRICE
    # ============================================================

    if unit_price is False and not reference_df.empty:

        # Convert date columns
        reference_df["_date"] = pd.to_datetime(
            reference_df["date"],
            errors="coerce"
        )

        current_date = pd.to_datetime(
            row["date"],
            errors="coerce"
        )

        if pd.notna(current_date):

            # Look within 30 days
            nearby = reference_df[
                (
                    reference_df["_date"]
                    .sub(current_date)
                    .abs()
                    <= pd.Timedelta(days=30)
                )
            ]

        else:
            nearby = reference_df

        prices = pd.to_numeric(
            nearby["unit_price_toman"],
            errors="coerce"
        ).dropna()

        if not prices.empty:

            unit_price = round(
                prices.median()
            )
            logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": "unit_price_toman",
                    "before": "",
                    "after": unit_price,
                    "flag": "IMPUTED"
            }

        else:
            logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": "unit_price_toman",
                    "before": "",
                    "after": unit_price,
                    "flag": "UNKNOWN"
            }


    # ============================================================
    # 6. RECOVER DISCOUNT
    # ============================================================

    if discount is False and not reference_df.empty:

        # --------------------------------------------------------
        # Try using similar quantity
        # --------------------------------------------------------

        if quantity is not False:

            reference_df["_quantity"] = pd.to_numeric(
                reference_df["quantity"],
                errors="coerce"
            )

            # Similar = within ±20%
            min_quantity = quantity * 0.8
            max_quantity = quantity * 1.2

            similar_quantity = reference_df[
                (
                    reference_df["_quantity"]
                    >= min_quantity
                )
                &
                (
                    reference_df["_quantity"]
                    <= max_quantity
                )
            ]

            discounts = pd.to_numeric(
                similar_quantity["discount_percent"],
                errors="coerce"
            ).dropna()

            if not discounts.empty:

                discount = round(
                    discounts.median()
                )
                logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": "discount_percent",
                    "before": "",
                    "after": discount,
                    "flag": "IMPUTED"
                }
            else:
                logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": "discount_percent",
                    "before": "",
                    "after": discount,
                    "flag": "UNKNOWN"
                }   

        # --------------------------------------------------------
        # If quantity is unavailable, use total price similarity
        # --------------------------------------------------------

        if discount is False and total_price is not False:

            reference_df["_total_price"] = pd.to_numeric(
                reference_df["total_price_toman"],
                errors="coerce"
            )

            min_total = total_price * 0.8
            max_total = total_price * 1.2

            similar_total = reference_df[
                (
                    reference_df["_total_price"]
                    >= min_total
                )
                &
                (
                    reference_df["_total_price"]
                    <= max_total
                )
            ]

            discounts = pd.to_numeric(
                similar_total["discount_percent"],
                errors="coerce"
            ).dropna()

            if not discounts.empty:

                discount = round(
                    discounts.median()
                )
                logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": "discount_percent",
                    "before": "",
                    "after": unit_price,
                    "flag": "IMPUTED"
                }
            else:
                logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": "discount_percent",
                    "before": "",
                    "after": discount,
                    "flag": "UNKNOWN"
                }   

    # ============================================================
    # 7. RE-CHECK
    # ============================================================

    values = [
        quantity,
        unit_price,
        discount,
        total_price
    ]

    missing_count = sum(
        value is False
        for value in values
    )


    # ============================================================
    # 8. IF ONLY ONE VALUE IS NOW MISSING, CALCULATE IT
    # ============================================================

    if missing_count == 1:

        # Missing quantity
        if quantity is False:
            quantity = calculate_quantity(
                total_price,
                unit_price,
                discount
            )
            logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": "quantity",
                    "before": "",
                    "after": quantity,
                    "flag": "CALCULATED"
            }

        # Missing unit price
        elif unit_price is False:
            unit_price = calculate_unit_price(
                quantity,
                total_price,
                discount
            )
            logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": "unit_price_toman",
                    "before": "",
                    "after": unit_price,
                    "flag": "CALCULATED"
            }

        # Missing discount
        elif discount is False:

            if quantity * unit_price != 0:

                discount = round(
                    (1 - total_price / (quantity * unit_price))
                    * 100
                )
                logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": "discount_percent",
                    "before": "",
                    "after": discount,
                    "flag": "CALCULATED"
                }

        # Missing total price
        elif total_price is False:
            total_price = calculate_total(
                quantity,
                unit_price,
                discount
            )
            logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": "total_price_toman",
                    "before": "",
                    "after": total_price,
                    "flag": "CALCULATED"
            }


    # ============================================================
    # 9. RECOVER QUANTITY
    # ============================================================

    if quantity is False and not reference_df.empty:

        # If total price and/or discount are available,
        # find similar transactions.

        reference_df["_total_price"] = pd.to_numeric(
            reference_df["total_price_toman"],
            errors="coerce"
        )

        reference_df["_discount"] = pd.to_numeric(
            reference_df["discount_percent"],
            errors="coerce"
        )

        similar = reference_df.copy()

        # --------------------------------------------------------
        # Similar total price
        # --------------------------------------------------------

        if total_price is not False:

            similar = similar[
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

        # --------------------------------------------------------
        # Similar discount
        # --------------------------------------------------------

        if discount is not False:

            similar = similar[
                similar["_discount"] == discount
            ]

        quantities = pd.to_numeric(
            similar["quantity"],
            errors="coerce"
        ).dropna()

        # --------------------------------------------------------
        # Use median of similar transactions
        # --------------------------------------------------------

        if not quantities.empty:

            quantity = round(
                quantities.median()
            )
            logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": "quantity",
                    "before": "",
                    "after": quantity,
                    "flag": "IMPUTED"
            }

        # --------------------------------------------------------
        # If no similar records, use all same-product records
        # --------------------------------------------------------

        else:

            quantities = pd.to_numeric(
                reference_df["quantity"],
                errors="coerce"
            ).dropna()

            if not quantities.empty:

                quantity = round(
                    quantities.median()
                )
                logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": "quantity",
                    "before": "",
                    "after": quantity,
                    "flag": "IMPUTED"
                }


    # ============================================================
    # 10. RECOVER TOTAL PRICE
    # ============================================================

    if total_price is False and not reference_df.empty:

        reference_df["_quantity"] = pd.to_numeric(
            reference_df["quantity"],
            errors="coerce"
        )

        similar = reference_df.copy()

        # Same product already guaranteed

        # Similar quantity
        if quantity is not False:

            similar = similar[
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

        totals = pd.to_numeric(
            similar["total_price_toman"],
            errors="coerce"
        ).dropna()

        if not totals.empty:

            total_price = round(
                totals.median()
            )
            logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": "total_price_toman",
                    "before": "",
                    "after": total_price,
                    "flag": "IMPUTED"
            }


    # ============================================================
    # 11. FINAL CALCULATION
    # ============================================================

    values = [
        quantity,
        unit_price,
        discount,
        total_price
    ]

    missing_count = sum(
        value is False or value is None
        for value in values
    )

    # If exactly one remains, calculate it
    if missing_count == 1:

        if quantity is False or quantity is None:

            if (
                total_price is not False
                and unit_price is not False
                and discount is not False
            ):
                quantity = calculate_quantity(
                    total_price,
                    unit_price,
                    discount
                )
                logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": "quantity",
                    "before": "",
                    "after": quantity,
                    "flag": "CALCULATED"
                }

        elif unit_price is False or unit_price is None:

            if (
                quantity is not False
                and total_price is not False
                and discount is not False
            ):
                unit_price = calculate_unit_price(
                    quantity,
                    total_price,
                    discount
                )
                logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": "unit_price_toman",
                    "before": "",
                    "after": unit_price,
                    "flag": "CALCULATED"
                }

        elif discount is False or discount is None:

            if (
                quantity is not False
                and unit_price is not False
                and total_price is not False
            ):
                if quantity * unit_price != 0:

                    discount = round(
                        (
                            1 -
                            total_price /
                            (quantity * unit_price)
                        ) * 100
                    )
                    logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": "discount_percent",
                    "before": "",
                    "after": discount,
                    "flag": "CALCULATED"
                    }

        elif total_price is False or total_price is None:

            if (
                quantity is not False
                and unit_price is not False
                and discount is not False
            ):
                total_price = calculate_total(
                    quantity,
                    unit_price,
                    discount
                )
                logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": "total_price_toman",
                    "before": "",
                    "after": total_price,
                    "flag": "CALCULATED"
                }


    # ============================================================
    # 12. FINAL VALIDATION
    # ============================================================

    if quantity is False or quantity is None:
        return False

    if total_price is False or total_price is None:
        return False


    # If unit price or discount still cannot be recovered,
    # return False as well because we cannot produce a
    # complete QUDT record.
    if unit_price is False or unit_price is None:
        return False

    if discount is False or discount is None:
        return False


    # ============================================================
    # 13. RETURN
    # ============================================================

    return [
        int(quantity),
        int(unit_price),
        int(discount),
        int(total_price)
    ]

def is_consistent(
    quantity,
    unit_price_toman,
    discount_percent,
    total_price_toman
):
    expected_total = round(
        quantity
        * unit_price_toman
        * (1 - discount_percent / 100)
    )

    difference_percent = abs(
        total_price_toman - expected_total
    ) / expected_total * 100

    # Allow up to 5% difference
    if difference_percent > 5:
        logs.loc[len(logs)] = {
                    "date": datetime.now(),
                    "modified_field": "total_price_toman",
                    "before": total_price_toman,
                    "after": total_price_toman,
                    "flag": "INCONSISTENT"
                }
        return False

    return True

sales = pd.read_csv(SALES_FILE)
print(sales.head())
clean_sales = sales.copy()
clean_sales = clean_sales.iloc[0:0]
logs = pd.read_csv(LOGS_FILE)
products = pd.read_csv(PRODUCTS_FILE)
distributions = pd.read_csv(DISTRIBUTIONS_FILE)


sale_id=0
thedate=""
product_id=""
distribution_id=""
quantity=0
unit_price_toman=0
discount_percent=0
total_price_toman=0
results = []
consistency = True
for index, row in sales.iterrows():
    sale_id = check_sale_id(clean_sales, row, logs)
    thedate = check_date(row, logs)
    product_id = check_product_id(row, products, logs)
    distribution_id = check_distribution_id(row, distributions, logs)
    results = check_QUDT(row, sales, logs)
    quantity = results[0]
    unit_price_toman = results[1]
    discount_percent = results[2]
    total_price_toman = results[3]
    consistency = is_consistent(quantity, unit_price_toman, discount_percent, total_price_toman)
    clean_sales.loc[len(clean_sales)] = {
    "sale_id": sale_id,
    "date": thedate,
    "product_id": product_id,
    "distribution_ID": distribution_id,
    "quantity": quantity,
    "unit_price_toman": unit_price_toman,
    "discount_percent": discount_percent,
    "total_price_toman": total_price_toman,
    "is_consistent": consistency
    }

print(clean_sales.head())