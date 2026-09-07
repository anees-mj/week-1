import asyncio
import json
from pathlib import Path
from src.store.config import PRODUCTS_FILE, USERS_FILE
from src.store.database import AsyncSessionLocal
from src.store.models import ProductModel, UserModel, UserRole

async def migrate_data():
    async with AsyncSessionLocal() as session:
        # Migrate Users
        if USERS_FILE.exists():
            with open(USERS_FILE, "r") as f:
                users_data = json.load(f)
                for u in users_data:
                    # Check if user already exists
                    role = UserRole.ADMIN if u.get("role") == "admin" else UserRole.CUSTOMER
                    user = UserModel(
                        username=u["username"],
                        password=u["password"],
                        phone=u.get("phone", ""),
                        address=u.get("address", ""),
                        role=role
                    )
                    session.add(user)
            print("Users migrated.")

        # Migrate Products
        if PRODUCTS_FILE.exists():
            with open(PRODUCTS_FILE, "r") as f:
                products_data = json.load(f)
                for p in products_data:
                    product = ProductModel(
                        name=p["name"],
                        price=p["price"],
                        category=p.get("category", "General"),
                        stock=p.get("stock", 10)
                    )
                    session.add(product)
            print("Products migrated.")

        await session.commit()
        print("Data migration complete!")

if __name__ == "__main__":
    asyncio.run(migrate_data())