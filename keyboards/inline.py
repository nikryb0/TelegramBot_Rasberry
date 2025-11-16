# keyboards/inline.py
from datetime import date, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu() -> InlineKeyboardMarkup:
    """Главное меню пользователя после входа."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Заказать ягоды", callback_data="start_order")],
        [InlineKeyboardButton(text="🧺 Корзина", callback_data="view_cart")],
        [InlineKeyboardButton(text="📜 История заказов", callback_data="my_orders")],
        [InlineKeyboardButton(text="📦 Текущие заказы", callback_data="current_orders")],
        [InlineKeyboardButton(text="🛟 Поддержка", url="https://t.me/nikryb0")]
    ])


def get_date_keyboard(today: date) -> InlineKeyboardMarkup:
    """Генерирует клавиатуру с датами на 30 дней вперёд (по 3 в ряд)."""
    buttons = []
    row = []
    for i in range(1, 31):  # 30 дней вперёд
        delivery_day = today + timedelta(days=i)
        date_str = delivery_day.strftime("%d.%m.%Y")
        button = InlineKeyboardButton(text=date_str, callback_data=f"date_{date_str}")
        row.append(button)
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:  # Если остались кнопки в незавершённом ряду
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_time_keyboard() -> InlineKeyboardMarkup:
    """Генерирует клавиатуру со временем доставки с 10:00 до 20:00."""
    buttons = [
        [InlineKeyboardButton(text=f"{h:02d}:00", callback_data=f"time_{h:02d}:00")]
        for h in range(10, 21)  # 10:00 – 20:00 включительно
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_cancel_order_button(order_id: str) -> InlineKeyboardMarkup:
    """Кнопка для отмены конкретного заказа."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить заказ", callback_data=f"cancel_user_{order_id}")]
    ])