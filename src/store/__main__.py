import sys
from .services import AuthService, CatalogService, CartService, CheckoutService

def main():
    print("=== Welcome to the Clothing Store ===")
    user = None
    cart = CartService()

    # Onboarding Flow
    while not user:
        print("\n--- Welcome Menu ---")
        print("1. Login")
        print("2. Signup")
        print("3. Exit App")
        choice = input("Select an option: ").strip()

        if choice == "1":
            u = input("Username (or '0' to go back): ").strip()
            if u == '0':
                continue
            p = input("Password: ").strip()
            user = AuthService.login(u, p)
            if not user:
                print("Invalid credentials.")
        elif choice == "2":
            u = input("Choose Username (or '0' to go back): ").strip()
            if u == '0':
                continue
            p = input("Choose Password: ").strip()
            try:
                user = AuthService.signup(u, p)
                print("Account created!")
            except ValueError as e:
                print(e)
        elif choice == "3":
            print("Goodbye!")
            sys.exit()

    # Main Store Loop
    while True:
        print(f"\n--- Main Menu (Logged in as {user.username}) ---")
        print("1. Browse Catalog")
        print("2. View Cart")
        print("3. Logout & Exit")
        choice = input("Select option: ").strip()

        if choice == "1":
            browse_catalog(cart, user)
        elif choice == "2":
            manage_cart(cart, user)
        elif choice == "3":
            print("Thank you for visiting! Goodbye.")
            break

def browse_catalog(cart: CartService, user):
    while True:
        print("\n--- Browse Catalog ---")
        print("(Enter '0' to return to Main Menu at any prompt)")
        
        season = input("Season (Summer/Winter): ").capitalize().strip()
        if season == '0':
            return

        category = input("Category (Stitched/Unstitched): ").capitalize().strip()
        if category == '0':
            return

        products = CatalogService.filter_products(season, category)
        if not products:
            print("No products found for this selection.")
            cont = input("\n1. Try another category | 0. Back to Main Menu: ").strip()
            if cont == '0':
                return
            continue

        print("\n--- Available Products ---")
        for idx, p in enumerate(products, 1):
            print(f"{idx}. {p.name} ({p.pieces}, {p.fabric}) - PKR {p.price}")
        print("0. Back to Main Menu")

        p_choice = input("\nSelect product number: ").strip()
        if p_choice == '0':
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

        print(f"\nProduct Details: {selected_prod.name}")
        print(f"Available Sizes: {', '.join(selected_prod.sizes)}")
        size = input("Choose Size (or '0' to cancel): ").strip()
        if size == '0':
            continue

        try:
            qty_input = input("Quantity (or '0' to cancel): ").strip()
            if qty_input == '0':
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
            cart.add_item(selected_prod, size, qty)
            print(f"\nSUCCESS: Added {qty}x {selected_prod.name} ({size}) to your cart.")
            return
        elif action == "2":
            temp_cart = CartService()
            temp_cart.add_item(selected_prod, size, qty)
            if checkout(temp_cart, user):
                return
        elif action == "0":
            return

def manage_cart(cart: CartService, user):
    while True:
        if not cart.items:
            print("\nYour cart is empty.")
            return

        print("\n--- Your Cart ---")
        for idx, item in enumerate(cart.items, 1):
            print(f"{idx}. {item.product.name} ({item.selected_size}) x {item.quantity} = PKR {item.total_price:.2f}")
        print(f"Subtotal: PKR {cart.get_subtotal():.2f}")

        print("\n1. Proceed to Checkout")
        print("2. Remove an Item")
        print("0. Back to Main Menu")
        choice = input("Select option: ").strip()

        if choice == "1":
            if checkout(cart, user):
                return
        elif choice == "2":
            item_no = input("Enter item number to remove (or '0' to cancel): ").strip()
            if item_no == '0':
                continue
            try:
                idx = int(item_no) - 1
                cart.remove_item(idx)
                print("Item removed successfully.")
            except ValueError:
                print("Invalid item number.")
        elif choice == "0":
            return

def checkout(cart: CartService, user) -> bool:
    print("\n--- Checkout ---")
    print("(Enter '0' at any prompt to cancel checkout)")

    phone = input("Contact Number: ").strip()
    if phone == '0':
        print("Checkout canceled.")
        return False

    address = input("Delivery Address: ").strip()
    if address == '0':
        print("Checkout canceled.")
        return False

    CheckoutService.process_checkout(cart, user, phone, address)
    return True

if __name__ == "__main__":
    main()