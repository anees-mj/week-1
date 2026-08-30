import json
import os
from typing import List, Optional
from .models import Product, CartItem, User
from .logger import logger
from .config import PRODUCTS_FILE, USERS_FILE, DELIVERY_CHARGES, CURRENCY, DEFAULT_PAYMENT_METHOD

class AuthService:
    @staticmethod
    def _load_users() -> list:
        if not os.path.exists(USERS_FILE):
            return []
        with open(USERS_FILE, "r") as f:
            return json.load(f)

    @classmethod
    def signup(cls, username: str, password: str) -> User:
        users = cls._load_users()
        if any(u["username"] == username for u in users):
            logger.warning(f"Failed signup attempt: Username '{username}' already exists.")
            raise ValueError("Username already exists.")
        new_user = {"username": username, "password": password, "phone": "", "address": ""}
        users.append(new_user)
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)
        logger.info(f"New user registered: {username}")
        return User(username, password)

    @classmethod
    def login(cls, username: str, password: str) -> Optional[User]:
        users = cls._load_users()
        for u in users:
            if u["username"] == username and u["password"] == password:
                logger.info(f"User logged in: {username}")
                return User(u["username"], u["password"], u.get("phone", ""), u.get("address", ""))
        logger.warning(f"Failed login attempt for username: {username}")
        return None

class CatalogService:
    @staticmethod
    def get_products() -> List[Product]:
        if not os.path.exists(PRODUCTS_FILE):
            return []
        with open(PRODUCTS_FILE, "r") as f:
            data = json.load(f)
        return [Product(**p) for p in data]

    @classmethod
    def filter_products(cls, season: str, category: str) -> List[Product]:
        logger.info(f"Catalog filtered by Season: {season}, Category: {category}")
        return [
            p for p in cls.get_products() 
            if p.season.lower() == season.lower() and p.category.lower() == category.lower()
        ]

class CartService:
    def __init__(self):
        self.items: List[CartItem] = []

    def add_item(self, product: Product, size: str, quantity: int):
        for item in self.items:
            if item.product.id == product.id and item.selected_size == size:
                item.quantity += quantity
                logger.info(f"Updated quantity in cart: {product.name} ({size}) x{item.quantity}")
                return
        self.items.append(CartItem(product, size, quantity))
        logger.info(f"Added to cart: {product.name} ({size}) x{quantity}")

    def remove_item(self, index: int):
        if 0 <= index < len(self.items):
            removed = self.items.pop(index)
            logger.info(f"Removed from cart: {removed.product.name}")

    def get_subtotal(self) -> float:
        return sum(item.total_price for item in self.items)

    def clear(self):
        self.items.clear()

class CheckoutService:
    @classmethod
    def process_checkout(cls, cart: CartService, user: User, phone: str, address: str):
        subtotal = cart.get_subtotal()
        total = subtotal + DELIVERY_CHARGES
        
        print("\n--- Order Summary ---")
        print(f"Customer: {user.username}")
        print(f"Delivery Address: {address} | Phone: {phone}")
        print(f"Subtotal: {CURRENCY} {subtotal:.2f}")
        print(f"Delivery Charges: {CURRENCY} {DELIVERY_CHARGES:.2f}")
        print(f"Grand Total: {CURRENCY} {total:.2f}")
        print(f"Payment Method: {DEFAULT_PAYMENT_METHOD}")
        print("\nOrder placed successfully!")
        
        logger.info(f"Order completed for {user.username}. Total Amount: {CURRENCY} {total:.2f}")
        cart.clear()