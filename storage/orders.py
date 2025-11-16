# storage/orders.py
import json
from pathlib import Path
from typing import Dict, List, Any

# Путь к файлу с заказами
ORDERS_FILE = Path("orders.json")


def load_orders() -> Dict[str, Any]:
    """
    Загружает данные заказов из orders.json.
    Если файл не существует или повреждён — создаёт новый с пустой структурой.
    """
    if not ORDERS_FILE.exists():
        # Инициализация пустого файла
        default_data = {"last_id": 0, "orders": {}}
        save_orders(default_data)
        return default_data

    try:
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Проверка структуры (на случай ручного редактирования)
            if "last_id" not in data or "orders" not in data:
                raise ValueError("Invalid structure")
            return data
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"⚠️ Ошибка чтения orders.json: {e}. Создаём новый файл.")
        default_data = {"last_id": 0, "orders": {}}
        save_orders(default_data)
        return default_data


def save_orders(data: Dict[str, Any]) -> None:
    """
    Сохраняет данные заказов в orders.json с форматированием.
    """
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def is_duplicate_order(cart: List[Dict], user_id: int, target_date: str) -> bool:
    """
    Проверяет, есть ли у пользователя уже оформленный заказ
    с таким же составом корзины на указанную дату.
    Сравнение — по сортированному списку ягод (игнорирует порядок).
    """
    orders_data = load_orders()
    cart_sorted = sorted(cart, key=lambda x: x["berry"])

    for order in orders_data["orders"].values():
        if (
            order["user_id"] == user_id
            and order["date"] == target_date
            and order["status"] != "отменён"
        ):
            order_cart_sorted = sorted(order["cart"], key=lambda x: x["berry"])
            if cart_sorted == order_cart_sorted:
                return True
    return False