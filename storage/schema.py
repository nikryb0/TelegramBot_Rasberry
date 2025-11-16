# storage/schema.py
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CartItem:
    berry: str
    kg: float
    price_per_kg: int
    total_price: float

    def __post_init__(self):
        # Приведение типов на случай загрузки из JSON (где всё — str)
        self.kg = float(self.kg)
        self.price_per_kg = int(self.price_per_kg)
        self.total_price = float(self.total_price)


@dataclass
class Order:
    user_id: int
    full_name: str
    phone: str
    cart: List[CartItem]
    date: str          # Формат: "dd.mm.YYYY"
    time: str          # Формат: "HH:MM"
    status: str        # "ожидает оплату", "оплачено", "отменён"

    def __post_init__(self):
        if isinstance(self.cart[0], dict):
            self.cart = [CartItem(**item) for item in self.cart]
        self.user_id = int(self.user_id)


@dataclass
class OrdersData:
    last_id: int
    orders: dict      # ключ — str(order_id), значение — Order

    def __post_init__(self):
        self.last_id = int(self.last_id)
        # Преобразуем сырые dict-ы в объекты Order
        new_orders = {}
        for oid, order_dict in self.orders.items():
            if isinstance(order_dict, dict):
                new_orders[oid] = Order(**order_dict)
            else:
                new_orders[oid] = order_dict  # уже объект
        self.orders = new_orders


@dataclass
class User:
    user_id: int
    full_name: str
    phone: str

    def __post_init__(self):
        self.user_id = int(self.user_id)