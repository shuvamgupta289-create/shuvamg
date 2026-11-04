from .admin import admin_bp, register_admin_cli
from .admin_inventory import admin_inventory_bp
from .admin_orders import admin_orders_bp
from .admin_products import admin_products_bp
from .checkout import checkout_bp
from .customer_auth import customer_auth_bp
from .customer_shopping import customer_shopping_bp
from .main import main_bp

__all__ = [
    "admin_bp",
    "admin_inventory_bp",
    "admin_orders_bp",
    "admin_products_bp",
    "checkout_bp",
    "customer_auth_bp",
    "customer_shopping_bp",
    "main_bp",
    "register_admin_cli",
]
