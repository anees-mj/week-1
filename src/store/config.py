from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = BASE_DIR / "data"
PRODUCTS_FILE = DATA_DIR / "products.json"
USERS_FILE = DATA_DIR / "users.json"

LOGS_DIR = BASE_DIR / "logs"
LOG_FILE = LOGS_DIR / "app.log"

DELIVERY_CHARGES = 250.0
CURRENCY = "PKR"
DEFAULT_PAYMENT_METHOD = "Cash on Delivery "

DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)