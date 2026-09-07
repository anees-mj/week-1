import hashlib
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import UserModel, ProductModel, OrderModel, OrderItemModel, OrderStatus, UserRole
from .exceptions import AuthenticationError, CartError

class AuthService:
    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    @classmethod
    async def login(cls, session: AsyncSession, username: str, password: str) -> UserModel:
        hashed = cls._hash_password(password)
        # Use UserModel.password instead of UserModel.password_hash
        stmt = select(UserModel).where(UserModel.username == username, UserModel.password == hashed)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise AuthenticationError("Invalid username or password.")
        return user

    @classmethod
    async def signup(cls, session: AsyncSession, username: str, password: str, role: UserRole = UserRole.CUSTOMER) -> UserModel:
        stmt = select(UserModel).where(UserModel.username == username)
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            raise AuthenticationError("Username already exists.")

        new_user = UserModel(
            username=username,
            password=cls._hash_password(password),  # Use password field
            role=role
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    
class CatalogService:
    @staticmethod
    async def filter_products(session: AsyncSession, season: str, category: str) -> List[ProductModel]:
        stmt = select(ProductModel).where(
            ProductModel.category.ilike(f"%{category}%")
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

class CartItem:
    def __init__(self, product: ProductModel, quantity: int):
        self.product = product
        self.quantity = quantity

    @property
    def total_price(self) -> float:
        return self.product.price * self.quantity

class CartService:
    def __init__(self):
        self.items: List[CartItem] = []

    def add_item(self, product: ProductModel, quantity: int):
        self.items.append(CartItem(product, quantity))

    def remove_item(self, index: int):
        if 0 <= index < len(self.items):
            self.items.pop(index)

    def get_subtotal(self) -> float:
        return sum(item.total_price for item in self.items)

    def clear(self):
        self.items.clear()

class CheckoutService:
    @staticmethod
    async def process_checkout(session: AsyncSession, cart: CartService, user: UserModel, phone: str, address: str) -> OrderModel:
        if not cart.items:
            raise CartError("Cart is empty.")

        user.phone = phone
        user.address = address

        order = OrderModel(
            user_id=user.id,
            total_amount=cart.get_subtotal(),
            status=OrderStatus.PENDING
        )
        session.add(order)
        await session.flush()

        for item in cart.items:
            if item.product.stock < item.quantity:
                raise CartError(f"Insufficient stock for {item.product.name}.")
            item.product.stock -= item.quantity
            order_item = OrderItemModel(
                order_id=order.id,
                product_id=item.product.id,
                quantity=item.quantity,
                unit_price=item.product.price
            )
            session.add(order_item)

        await session.commit()
        await session.refresh(order)
        cart.clear()
        return order

class OrderService:
    @staticmethod
    async def get_user_orders(session: AsyncSession, user: UserModel) -> List[OrderModel]:
        stmt = select(OrderModel).where(OrderModel.user_id == user.id)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_order_by_id(session: AsyncSession, order_id: int, user: UserModel) -> Optional[OrderModel]:
        stmt = select(OrderModel).where(OrderModel.id == order_id)
        result = await session.execute(stmt)
        order = result.scalar_one_or_none()

        if order and (user.role == UserRole.ADMIN or order.user_id == user.id):
            return order
        return None

    @staticmethod
    async def admin_update_order_status(session: AsyncSession, admin: UserModel, order_id: int, new_status: OrderStatus) -> OrderModel:
        if admin.role != UserRole.ADMIN:
            raise AuthenticationError("Only administrators can update order statuses.")

        stmt = select(OrderModel).where(OrderModel.id == order_id)
        result = await session.execute(stmt)
        order = result.scalar_one_or_none()

        if not order:
            raise ValueError(f"Order #{order_id} not found.")

        order.status = new_status
        await session.commit()
        await session.refresh(order)
        return order