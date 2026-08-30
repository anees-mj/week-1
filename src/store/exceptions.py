class StoreException(Exception): pass
class AuthenticationError(StoreException): pass
class CartError(StoreException): pass