# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# متغیرهای دیتابیس
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')  # پیش‌فرض 5432
DB_NAME = os.getenv('DB_NAME', 'whitex')
DB_USER = os.getenv('DB_USER', 'whitex')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'whitex_password')

# ساخت DATABASE_URL از روی متغیرها
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# یا اگر میخواید مستقیم کل URL رو از env بگیرید:
# DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg2://whitex:whitex_password@localhost:5432/whitex')