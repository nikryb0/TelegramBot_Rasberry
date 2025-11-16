# main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import (
    common_router,
    start_router,
    order_router,
    user_menu_router,
    admin_router
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Подключаем ТОЛЬКО роутеры — НИКАКИХ dp.message.register!
    dp.include_router(common_router)
    dp.include_router(start_router)       # ← содержит /start И handle_contact
    dp.include_router(order_router)
    dp.include_router(user_menu_router)
    dp.include_router(admin_router)

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("✅ Бот 'Ягодки' запущен и готов принимать заказы!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен вручную.")
    except Exception as e:
        logger.critical(f"❌ Критическая ошибка: {e}", exc_info=True)