from dataclasses import dataclass
from typing import List

@dataclass
class Product:
    id: str
    name: str
    season: str
    category: str
    pieces: str
    fabric: str
    sizes: List[str]
    price: float

@dataclass
class CartItem:
    product: Product
    selected_size: str
    quantity: int

    @property
    def total_price(self) -> float:
        return self.product.price * self.quantity

@dataclass
class User:
    username: str
    password: str
    phone: str = ""
    address: str = ""