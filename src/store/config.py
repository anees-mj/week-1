import os
from pathlib import Path

# Base Directory (Project Root directory)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Data Paths
DATA_DIR = BASE_DIR / "data"
PRODUCTS_FILE = DATA_DIR / "products.json"
USERS_FILE = DATA_DIR / "users.json"

# Logging Paths
LOGS_DIR = BASE_DIR / "logs"
LOG_FILE = LOGS_DIR / "app.log"

# Application Business Logic Settings
DELIVERY_CHARGES = 250.0
CURRENCY = "PKR"
DEFAULT_PAYMENT_METHOD = "Cash on Delivery (COD)"

# Ensure required storage directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)