from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# JSON File Paths for Legacy Data Migration
PRODUCTS_FILE = DATA_DIR / "products.json"
USERS_FILE = DATA_DIR / "users.json"

# Async SQLite Database URI
DATABASE_URL = f"sqlite+aiosqlite:///{DATA_DIR / 'store.db'}"

DELIVERY_CHARGES = 250.0
CURRENCY = "PKR"
DEFAULT_PAYMENT_METHOD = "Cash on Delivery (COD)"