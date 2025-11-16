# handlers/admin.py
from aiogram import Router, F, Bot
from aiogram.types import Message
from collections import defaultdict
from datetime import datetime


from config import ADMIN_ID
from storage.users import load_users
from storage.orders import load_orders, save_orders

# Создаём роутер и применяем фильтр: обрабатывать сообщения только от админа
router = Router(name="admin")
router.message.filter(F.from_user.id == ADMIN_ID)


@router.message(F.text.startswith("/oplata"))
async def cmd_payment(message: Message, bot: Bot):
    parts = message.text.split(" ", 2)
    if len(parts) != 3 or not parts[1].isdigit():
        await message.answer("❌ Неверный формат.\nИспользуйте: /oplata <номер_заказа> <ссылка_на_оплату>")
        return

    order_id, payment_link = parts[1], parts[2]
    orders_data = load_orders()
    order = orders_data["orders"].get(order_id)

    if not order:
        await message.answer(f"Заказ №{order_id} не найден.")
        return

    if order["status"] == "оплачено":
        await message.answer(f"Заказ №{order_id} уже оплачен.")
        return

    try:
        await bot.send_message(
            order["user_id"],
            f"💳 Ссылка на оплату для заказа №{order_id}:\n{payment_link}\n\n"
            f"После оплаты с вами свяжется менеджер."
        )
    except Exception as e:
        await message.answer(f"⚠️ Не удалось отправить сообщение пользователю: {e}")
        return

    # Обновляем статус заказа
    order["status"] = "оплачено"
    save_orders(orders_data)
    await message.answer(f"✅ Ссылка на оплату отправлена клиенту заказа №{order_id}.")


@router.message(F.text.startswith("/cancel_order_admin"))
async def cmd_cancel_order_admin(message: Message, bot: Bot):
    parts = message.text.strip().split(" ", 2)
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("❌ Неверный формат.\nИспользуйте: /cancel_order_admin <номер_заказа> [причина]")
        return

    order_id = parts[1]
    reason = parts[2] if len(parts) > 2 else "Причина не указана"

    orders_data = load_orders()
    order = orders_data["orders"].get(order_id)

    if not order:
        await message.answer(f"Заказ №{order_id} не найден.")
        return

    if order["status"] == "отменён":
        await message.answer(f"Заказ №{order_id} уже отменён.")
        return

    # Отменяем заказ
    order["status"] = "отменён"
    save_orders(orders_data)

    # Уведомляем клиента
    try:
        await bot.send_message(
            order["user_id"],
            f"❌ Ваш заказ №{order_id} был отменён администратором.\nПричина: {reason}"
        )
    except Exception as e:
        await message.answer(f"⚠️ Не удалось уведомить пользователя: {e}")

    await message.answer(f"✅ Заказ №{order_id} успешно отменён.\nПричина: {reason}")

@router.message(F.text == "/admin_orders")
async def cmd_admin_orders(message: Message):
    try:
        orders_data = load_orders()
        orders = orders_data["orders"]
        if not orders:
            await message.answer("📦 Нет заказов.")
            return

        response = "📋 Все заказы:\n\n"
        for order_id, order in sorted(orders.items(), key=lambda x: int(x[0]), reverse=True):
            status = order["status"]
            total = sum(item["total_price"] for item in order["cart"])
            response += (
                f"№{order_id} | {order['full_name']} | +7{order['phone'][-10:]}\n"
                f"📅 {order['date']} в {order['time']} | 💰 {round(total, 2)}₽ | 📌 {status}\n\n"
            )
        await message.answer(response)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@router.message(F.text == "/admin_slots")
async def cmd_admin_slots(message: Message):
    try:
        orders_data = load_orders()
        slots = defaultdict(list)

        for order_id, order in orders_data["orders"].items():
            if order["status"] != "отменён":
                slots[order["date"]].append(order["time"])

        if not slots:
            await message.answer("📅 Нет активных слотов.")
            return

        response = "🗓 Занятые слоты доставки:\n\n"
        for date in sorted(slots.keys(), key=lambda x: datetime.strptime(x, "%d.%m.%Y")):
            times = sorted(slots[date])
            response += f"📅 {date}: {', '.join(times)}\n"
        await message.answer(response)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

# В handlers/admin.py

@router.message(F.text == "/admin_stats")
async def cmd_admin_stats(message: Message):
    try:
        orders_data = load_orders()
        orders = [o for o in orders_data["orders"].values() if o["status"] == "оплачено"]
        total_revenue = sum(sum(item["total_price"] for item in o["cart"]) for o in orders)
        total_orders = len(orders)

        # ТОП ягод
        berry_sales = defaultdict(float)
        for order in orders:
            for item in order["cart"]:
                berry_sales[item["berry"]] += item["kg"]

        top_berries = sorted(berry_sales.items(), key=lambda x: x[1], reverse=True)[:3]

        response = (
            f"📊 Статистика продаж:\n\n"
            f"🛒 Всего оплачено заказов: {total_orders}\n"
            f"💰 Общая выручка: {round(total_revenue, 2)}₽\n\n"
            f"🏆 ТОП-3 ягоды по объёму:\n"
        )
        for i, (berry, kg) in enumerate(top_berries, 1):
            response += f"{i}. {berry} — {kg} кг\n"

        await message.answer(response)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

# В handlers/admin.py

@router.message(F.text.startswith("/admin_broadcast"))
async def cmd_admin_broadcast(message: Message, bot: Bot):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        await message.answer("Используйте: /admin_broadcast [текст рассылки]")
        return

    text = parts[1]
    users = load_users()
    if not users:
        await message.answer("📭 Нет пользователей для рассылки.")
        return

    success = 0
    failed = 0
    for user_data in users.values():
        try:
            await bot.send_message(user_data["user_id"], f"📢 Рассылка:\n\n{text}")
            success += 1
        except Exception:
            failed += 1

    await message.answer(f"✅ Рассылка завершена!\nУспешно: {success}, Неудачно: {failed}")