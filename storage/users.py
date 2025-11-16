# storage/users.py
import json
from pathlib import Path
from typing import Dict, Any

# Путь к файлу с пользователями
USERS_FILE = Path("users.json")


def load_users() -> Dict[str, Any]:
    """
    Загружает пользователей из users.json.
    Если файл не существует — возвращает пустой словарь.
    Если файл повреждён — создаёт резервную копию и возвращает пустой словарь.
    """
    if not USERS_FILE.exists():
        return {}

    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Убедимся, что это словарь
            if not isinstance(data, dict):
                raise ValueError("users.json должен содержать объект (словарь).")
            return data
    except (json.JSONDecodeError, ValueError, OSError) as e:
        print(f"⚠️ Ошибка чтения users.json: {e}. Данные не загружены.")
        # Опционально: создать резервную копию повреждённого файла
        try:
            USERS_FILE.rename(USERS_FILE.with_suffix(".json.corrupted"))
        except Exception:
            pass
        return {}


def save_user(phone: str, user_id: int, full_name: str) -> None:
    """
    Сохраняет или обновляет данные пользователя по номеру телефона.
    Формат записи:
    {
      "9001234567": {
        "user_id": 123456789,
        "full_name": "Иванов Иван Иванович",
        "phone": "9001234567"
      }
    }
    """
    users = load_users()
    users[phone] = {
        "user_id": user_id,
        "full_name": full_name,
        "phone": phone
    }
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Ошибка сохранения users.json: {e}")
        raise