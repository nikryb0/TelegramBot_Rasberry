# utils/helpers.py
import re


def extract_berry_name(text: str) -> str:
    """
    Извлекает название ягоды из строки вида "Голубика — 500₽".
    Если формат не распознан — возвращает исходную строку.
    """
    # Ищем всё до первого вхождения " — " (с пробелами)
    match = re.match(r"^(.*?)\s*—", text)
    if match:
        berry = match.group(1).strip()
        return berry
    return text


def get_user_role(user_id: int, admin_id: int, helper_ids: list) -> str:
    """
    Определяет роль пользователя по ID.
    """
    if user_id == admin_id:
        return "admin"
    elif user_id in helper_ids:
        return "helper"
    else:
        return "user"