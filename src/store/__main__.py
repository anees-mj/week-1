import asyncio
import sys
from typing import Optional

from .database import AsyncSessionLocal
from .exceptions import AuthenticationError, CartError
from .models import OrderStatus, UserModel, UserRole
from .services import AuthService, CartService, CatalogService, CheckoutService, OrderService


async def main():
    print("=== Welcome to the Clothing Store ===")
    user: Optional[UserModel] = None
    cart = CartService()

    async with AsyncSessionLocal() as session:
        # 1. Welcome / Auth Menu Loop
        while not user:
            print("\n--- Welcome Menu ---")
            print("1. Login")
            print("2. Signup")
            print("3. Exit App")
            choice = input("Select an option: ").strip()

            if choice == "1":
                u = input("Username (or '0' to go back): ").strip()
                if u == "0":
                    continue
                p = input("Password: ").strip()
                try:
                    user = await AuthService.login(session, u, p)
                    print(f"\nWelcome back, {user.username}!")
                except AuthenticationError as e:
                    print(f"\nError: {e}")

            elif choice == "2":
                u = input("Choose Username (or '0' to go back): ").strip()
                if u == "0":
                    continue
                p = input("Choose Password: ").strip()
                try:
                    user = await AuthService.signup(session, u, p)
                    print("\nAccount created successfully!")
                except (AuthenticationError, ValueError) as e:
                    print(f"\nError: {e}")

            elif choice == "3":
                print("Goodbye!")
                sys.exit()

        # 2. Main Menu Loop (Role-Aware)
        while True:
            print(f"\n--- Main Menu (Logged in as {user.username} | Role: {user.role.value}) ---")
            print("1. Browse Catalog")
            print("2. View Cart")
            print("3. Order Tracking (My Orders)")

            if user.role == UserRole.ADMIN:
                print("4. Admin Dashboard (Manage All Orders)")

            print("0. Logout & Exit")
            choice = input("Select option: ").strip()

            if choice == "1":
                await browse_catalog(session, cart, user)
            elif choice == "2":
                await manage_cart(session, cart, user)
            elif choice == "3":
                await view_user_orders(session, user)
            elif choice == "4" and user.role == UserRole.ADMIN:
                await admin_dashboard(session, user)
            elif choice == "0":
                print("Thank you for visiting! Goodbye.")
                break


async def browse_catalog(session, cart: CartService, user: UserModel):
    while True:
        print("\n--- Browse Catalog ---")
        print("(Enter '0' to return to Main Menu at any prompt)")

        season = input("Season (Summer/Winter): ").capitalize().strip()
        if season == "0":
            return

        category = input("Category (Stitched/Unstitched): ").capitalize().strip()
        if category == "0":
            return

        products = await CatalogService.filter_products(session, season, category)
        if not products:
            print("No products found for this selection.")
            cont = input("\n1. Try another category | 0. Back to Main Menu: ").strip()
            if cont == "0":
                return
            continue

        print("\n--- Available Products ---")
        for idx, p in enumerate(products, 1):
            print(f"{idx}. {p.name} - PKR {p.price:.2f} (Stock: {p.stock})")
        print("0. Back to Main Menu")

        p_choice = input("\nSelect product number: ").strip()
        if p_choice == "0":
            return

        try:
            p_idx = int(p_choice) - 1
            if p_idx < 0 or p_idx >= len(products):
                print("Invalid selection.")
                continue
            selected_prod = products[p_idx]
        except ValueError:
            print("Please enter a valid number.")
            continue

        try:
            qty_input = input("Quantity (or '0' to cancel): ").strip()
            if qty_input == "0":
                continue
            qty = int(qty_input)
            if qty <= 0:
                print("Quantity must be greater than 0.")
                continue
        except ValueError:
            print("Invalid quantity.")
            continue

        print("\n1. Add to Cart")
        print("2. Buy Now (Direct Checkout)")
        print("0. Cancel / Back to Main Menu")
        action = input("Select action: ").strip()

        if action == "1":
            cart.add_item(selected_prod, qty)
            print(f"\nSUCCESS: Added {qty}x {selected_prod.name} to your cart.")
            return
        elif action == "2":
            temp_cart = CartService()
            temp_cart.add_item(selected_prod, qty)
            if await checkout(session, temp_cart, user):
                return
        elif action == "0":
            return


async def manage_cart(session, cart: CartService, user: UserModel):
    while True:
        if not cart.items:
            print("\nYour cart is empty.")
            return

        print("\n--- Your Cart ---")
        for idx, item in enumerate(cart.items, 1):
            print(f"{idx}. {item.product.name} x {item.quantity} = PKR {item.total_price:.2f}")
        print(f"Subtotal: PKR {cart.get_subtotal():.2f}")

        print("\n1. Proceed to Checkout")
        print("2. Remove an Item")
        print("0. Back to Main Menu")
        choice = input("Select option: ").strip()

        if choice == "1":
            if await checkout(session, cart, user):
                return
        elif choice == "2":
            item_no = input("Enter item number to remove (or '0' to cancel): ").strip()
            if item_no == "0":
                continue
            try:
                idx = int(item_no) - 1
                cart.remove_item(idx)
                print("Item removed successfully.")
            except (ValueError, IndexError):
                print("Invalid item number.")
        elif choice == "0":
            return


async def checkout(session, cart: CartService, user: UserModel) -> bool:
    print("\n--- Checkout ---")
    print("(Enter '0' at any prompt to cancel checkout)")

    phone = input(f"Contact Number [{user.phone or 'N/A'}]: ").strip()
    if phone == "0":
        print("Checkout canceled.")
        return False
    phone = phone if phone else user.phone

    address = input(f"Delivery Address [{user.address or 'N/A'}]: ").strip()
    if address == "0":
        print("Checkout canceled.")
        return False
    address = address if address else user.address

    try:
        order = await CheckoutService.process_checkout(session, cart, user, phone, address)
        print(f"\nSUCCESS: Order #{order.id} placed! Status: {order.status.value}")
        return True
    except CartError as e:
        print(f"\nCheckout Failed: {e}")
        return False


async def view_user_orders(session, user: UserModel):
    """Customer View: View logged-in user's orders and real-time status."""
    orders = await OrderService.get_user_orders(session, user)
    print("\n--- My Orders ---")
    if not orders:
        print("No order history found.")
        return

    for o in orders:
        print(f"Order #{o.id} | Date: {o.created_at.strftime('%Y-%m-%d %H:%M')} | Total: PKR {o.total_amount:.2f} | Status: [{o.status.value}]")
    input("\nPress Enter to return to Main Menu...")


async def admin_dashboard(session, admin_user: UserModel):
    """Admin View: Retrieve any order and update status."""
    print("\n--- Admin Order Dashboard ---")
    order_id_input = input("Enter Order ID to view/update (or '0' to cancel): ").strip()
    if order_id_input == "0":
        return

    try:
        order_id = int(order_id_input)
        order = await OrderService.get_order_by_id(session, order_id, admin_user)
        if not order:
            print(f"Order #{order_id} not found.")
            return

        print(f"\nOrder #{order.id} | User ID: {order.user_id} | Current Status: {order.status.value}")
        print("Select New Status:")
        print("1. PENDING\n2. PROCESSING\n3. SHIPPED\n4. DELIVERED\n5. CANCELLED\n0. Keep Current")
        
        status_choice = input("Choice: ").strip()
        status_map = {
            "1": OrderStatus.PENDING,
            "2": OrderStatus.PROCESSING,
            "3": OrderStatus.SHIPPED,
            "4": OrderStatus.DELIVERED,
            "5": OrderStatus.CANCELLED,
        }

        if status_choice in status_map:
            updated = await OrderService.admin_update_order_status(
                session, admin_user, order_id, status_map[status_choice]
            )
            print(f"SUCCESS: Order #{updated.id} status updated to {updated.status.value}")

    except AuthenticationError as e:
        print(f"Access Error: {e}")
    except ValueError:
        print("Invalid Order ID.")


if __name__ == "__main__":
    asyncio.run(main())