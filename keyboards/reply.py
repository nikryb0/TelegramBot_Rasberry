# keyboards/reply.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import BERRIES, BERRY_PRICES


def get_berry_keyboard() -> ReplyKeyboardMarkup:
    """
    Возвращает клавиатуру с ягодами и ценами + кнопку 'Завершить заказ'.
    """
    keyboard = []
    for berry in BERRIES:
        if berry == "Завершить заказ":
            # Кнопка завершения — без цены
            keyboard.append([KeyboardButton(text=berry)])
        else:
            # Формат: "Голубика — 500₽"
            price = BERRY_PRICES[berry]
            button_text = f"{berry} — {price}₽"
            keyboard.append([KeyboardButton(text=button_text)])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False  # чтобы клавиатура оставалась видимой при выборе нескольких ягод
    )