# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения из файла Bot_berries.env
env_path = Path("Bot_berries.env")
if not env_path.exists():
    raise FileNotFoundError(f"Файл конфигурации не найден: {env_path.resolve()}")

load_dotenv(env_path)

# === Обязательные параметры ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ Переменная BOT_TOKEN не задана в Bot_berries.env")

try:
    ADMIN_ID = int(os.getenv("ADMIN_ID", ""))
except (ValueError, TypeError):
    raise ValueError("❌ Переменная ADMIN_ID должна быть целым числом (ваш Telegram ID)")

# === Опциональные параметры ===
HELPER_IDS_RAW = os.getenv("HELPER_IDS", "")
HELPER_IDS = []
if HELPER_IDS_RAW.strip():
    try:
        HELPER_IDS = [int(x.strip()) for x in HELPER_IDS_RAW.split(",") if x.strip()]
    except ValueError:
        raise ValueError("❌ HELPER_IDS должен содержать целые числа, разделённые запятыми")

# === Константы ассортимента ===
BERRIES = [
    "Голубика", "Шелковица", "Черника", "Черешня",
    "Бузина", "Смородина чёрная", "Клюква", "Земляника", "Вишня", "Завершить заказ"
]

BERRY_PRICES = {
    "Голубика": 500,
    "Шелковица": 600,
    "Черника": 450,
    "Черешня": 400,
    "Бузина": 350,
    "Смородина чёрная": 380,
    "Клюква": 420,
    "Земляника": 380,
    "Вишня": 390,
}

# === Валидация ассортимента ===
for berry in BERRY_PRICES:
    if berry not in BERRIES or berry == "Завершить заказ":
        raise ValueError(f"❌ Несоответствие в ассортименте: '{berry}' есть в ценах, но отсутствует в списке BERRIES")

if "Завершить заказ" not in BERRIES:
    raise ValueError("❌ В списке BERRIES должна быть кнопка 'Завершить заказ'")