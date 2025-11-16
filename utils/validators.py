# utils/validators.py
import re


def is_valid_full_name(full_name: str) -> bool:
    """
    Проверяет, соответствует ли строка формату ФИО:
    - Три слова на кириллице
    - Каждое слово начинается с заглавной буквы
    - Без цифр и спецсимволов (кроме дефиса внутри слова, например: "Иванов-Петров")

    Примеры валидных: "Иванов Иван Иванович", "Мария-Елена Сидорова Петровна"
    """
    if not isinstance(full_name, str):
        return False

    # Разрешаем дефис внутри слова: [А-ЯЁ][а-яё]+(?:-[А-ЯЁ][а-яё]+)*
    name_part = r"[А-ЯЁ][а-яё]+(?:-[А-ЯЁ][а-яё]+)*"
    full_pattern = rf"^{name_part} {name_part} {name_part}$"

    return bool(re.fullmatch(full_pattern, full_name.strip()))


def normalize_phone(raw_phone: str) -> str:
    """
    Нормализует телефонный номер к формату из 10 цифр (без +, 7, 8).
    Поддерживаемые входные форматы:
      +79001234567
      89001234567
      9001234567
      79001234567

    Возвращает строку из 10 цифр или исходную строку, если не удалось нормализовать.
    """
    if not isinstance(raw_phone, str):
        return raw_phone

    # Удаляем все нецифровые символы
    digits = re.sub(r"\D", "", raw_phone)

    # Обрабатываем стандартные случаи
    if len(digits) == 11 and digits.startswith(("7", "8")):
        return digits[1:]  # отбрасываем первый символ (7 или 8)
    elif len(digits) == 10:
        return digits
    elif len(digits) == 12 and digits.startswith("375"):
        # Опционально: поддержка Беларуси (+375) → оставляем как есть или обрезаем
        return digits  # или обработать отдельно
    else:
        # Неизвестный формат — возвращаем как есть (обработка на уровень выше)
        return raw_phone


def is_valid_russian_phone(phone: str) -> bool:
    """
    Проверяет, является ли нормализованный номер валидным российским номером (10 цифр).
    """
    normalized = normalize_phone(phone)
    return len(normalized) == 10 and normalized.isdigit()