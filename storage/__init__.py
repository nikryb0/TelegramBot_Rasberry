# storage/__init__.py

from .users import load_users, save_user
from .orders import load_orders, save_orders, is_duplicate_order