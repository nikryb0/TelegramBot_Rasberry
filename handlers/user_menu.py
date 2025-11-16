# handlers/user_menu.py
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery

from config import ADMIN_ID
from storage.orders import load_orders, save_orders

router = Router(name="user_menu")


def format_order(order_id: str, order: dict) -> str:
    """Форматирует заказ для отображения."""
    status_labels = {
        "ожидает оплату": "⏳ Ожидает оплаты",
        "оплачено": "✅ Оплачен",
        "отменён": "❌ Отменён"
    }
    status = status_labels.get(order["status"], order["status"])
    total = sum(item["total_price"] for item in order["cart"])
    berries = "\n".join([f"  • {item['berry']}: {item['kg']} кг" for item in order["cart"]])
    return (
        f"<b>Заказ №{order_id}</b>\n"
        f"📅 {order['date']} в {order['time']}\n"
        f"{berries}\n"
        f"💰 Итого: {round(total, 2)}₽\n"
        f"📌 {status}"
    )


# === История заказов ===
@router.callback_query(F.data == "my_orders")
@router.message(F.text == "/my_orders")
async def cmd_my_orders(event, bot: Bot = None):
    message = event.message if isinstance(event, CallbackQuery) else event
    user_id = message.from_user.id

    try:
        orders_data = load_orders()
        user_orders = [
            (oid, order)
            for oid, order in orders_data["orders"].items()
            if order["user_id"] == user_id
        ]

        if not user_orders:
            await message.answer("У вас пока нет заказов. 🛒")
            return

        # Сортируем по номеру заказа (по убыванию)
        user_orders.sort(key=lambda x: int(x[0]), reverse=True)

        from keyboards.inline import get_cancel_order_button

        for order_id, order in user_orders:
            text = format_order(order_id, order)
            if order["status"] in ("ожидает оплату", "оплачено"):
                await message.answer(
                    text,
                    reply_markup=get_cancel_order_button(order_id),
                    parse_mode="HTML"
                )
            else:
                await message.answer(text, parse_mode="HTML")

        if isinstance(event, CallbackQuery):
            await event.answer()

    except Exception as e:
        await message.answer(f"⚠️ Ошибка при загрузке заказов: {e}")


# === Текущие заказы (активные) ===
@router.callback_query(F.data == "current_orders")
async def current_orders(callback: CallbackQuery):
    user_id = callback.from_user.id
    try:
        orders_data = load_orders()
        current = []
        for oid, order in orders_data["orders"].items():
            if order["user_id"] == user_id and order["status"] in ("ожидает оплату", "оплачено"):
                status = "⏳" if order["status"] == "ожидает оплату" else "✅"
                current.append(f"{status} №{oid} — {order['date']} в {order['time']}")

        if not current:
            await callback.answer("У вас нет активных заказов.", show_alert=True)
        else:
            text = "📦 Ваши текущие заказы:\n" + "\n".join(current)
            await callback.answer(text, show_alert=True)

    except Exception:
        await callback.answer("❌ Не удалось загрузить заказы.", show_alert=True)


# === Отмена заказа через кнопку ===
@router.callback_query(F.data.startswith("cancel_user_"))
async def cancel_order_inline(callback: CallbackQuery, bot: Bot):
    order_id = callback.data.split("_")[-1]
    orders_data = load_orders()
    order = orders_data["orders"].get(order_id)

    if not order:
        await callback.answer("Заказ не найден.", show_alert=True)
        return

    if order["user_id"] != callback.from_user.id:
        await callback.answer("Вы не можете отменить чужой заказ.", show_alert=True)
        return

    if order["status"] == "отменён":
        await callback.answer("Этот заказ уже отменён.", show_alert=True)
        return

    # Отменяем заказ
    order["status"] = "отменён"
    save_orders(orders_data)

    # Обновляем сообщение
    await callback.message.edit_text(f"❌ Заказ №{order_id} отменён.")

    # Уведомляем админа
    try:
        await bot.send_message(ADMIN_ID, f"🔁 Пользователь отменил заказ №{order_id}")
    except Exception:
        pass  # Игнорируем ошибку отправки админу

    await callback.answer("Заказ успешно отменён.")


# === Отмена последнего активного заказа командой ===
@router.message(F.text == "/cancel_order")
async def cmd_cancel_order(message: Message, bot: Bot):
    user_id = message.from_user.id
    try:
        orders_data = load_orders()
        active_orders = [
            (oid, o)
            for oid, o in orders_data["orders"].items()
            if o["user_id"] == user_id and o["status"] in ("ожидает оплату", "оплачено")
        ]

        if not active_orders:
            await message.answer("У вас нет активных заказов для отмены.")
            return

        # Находим самый свежий заказ (по номеру)
        latest_id, _ = max(active_orders, key=lambda x: int(x[0]))
        orders_data["orders"][latest_id]["status"] = "отменён"
        save_orders(orders_data)

        await message.answer(f"❌ Заказ №{latest_id} отменён.")
        try:
            await bot.send_message(ADMIN_ID, f"🔁 Пользователь отменил заказ №{latest_id}")
        except Exception:
            pass

    except Exception as e:
        await message.answer(f"⚠️ Ошибка при отмене заказа: {e}")