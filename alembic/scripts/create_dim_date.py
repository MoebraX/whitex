from datetime import date, timedelta
import psycopg2
import jdatetime


START_DATE = date(2025, 1, 1)
END_DATE = date(2027, 12, 31)


conn = psycopg2.connect(
    host="localhost",
    port=5434,
    database="whitex",
    user="whitex",
    password="whitex_password"
)

cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS dim_date (

    date DATE PRIMARY KEY,

    -- Gregorian
    gregorian_year INTEGER,
    gregorian_month INTEGER,
    gregorian_month_name VARCHAR(20),
    gregorian_quarter INTEGER,

    -- Jalali
    jalali_year INTEGER,
    jalali_month INTEGER,
    jalali_month_name VARCHAR(20),
    jalali_quarter INTEGER,

    -- Week / Day
    week_number INTEGER,
    day INTEGER,
    day_name VARCHAR(20)

);
""")


jalali_months = [
    "فروردین",
    "اردیبهشت",
    "خرداد",
    "تیر",
    "مرداد",
    "شهریور",
    "مهر",
    "آبان",
    "آذر",
    "دی",
    "بهمن",
    "اسفند"
]


current = START_DATE


while current <= END_DATE:

    jalali = jdatetime.date.fromgregorian(date=current)


    cursor.execute(
        """
        INSERT INTO dim_date
        (
            date,

            gregorian_year,
            gregorian_month,
            gregorian_month_name,
            gregorian_quarter,

            jalali_year,
            jalali_month,
            jalali_month_name,
            jalali_quarter,

            week_number,
            day,
            day_name
        )

        VALUES
        (
            %s,%s,%s,%s,%s,
            %s,%s,%s,%s,
            %s,%s,%s
        )

        ON CONFLICT (date) DO NOTHING;
        """,
        (
            current,

            current.year,
            current.month,
            current.strftime("%B"),
            (current.month - 1)//3 + 1,

            jalali.year,
            jalali.month,
            jalali_months[jalali.month-1],
            (jalali.month - 1)//3 + 1,

            current.isocalendar().week,
            current.day,
            current.strftime("%A")
        )
    )


    current += timedelta(days=1)


conn.commit()

cursor.close()
conn.close()

print("dim_date created")