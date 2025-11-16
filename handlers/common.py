# handlers/common.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from config import ADMIN_ID
from keyboards.inline import get_main_menu

router = Router(name="common")


@router.message(F.text == "/help")
async def cmd_help(message: Message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        text = (
            "🛠 <b>Админка:</b>\n"
            "/oplata [номер] [ссылка] — отправить клиенту ссылку на оплату\n"
            "/cancel_order_admin [номер] [причина] — отменить заказ\n"
            "/admin_orders — список всех заказов\n"
            "/admin_slots — занятые даты и время доставки\n"
            "/admin_stats — статистика продаж\n"
            "/admin_broadcast [текст] — рассылка всем пользователям\n"
            "🛒 <b>Покупатель:</b>\n"
            "/start — начать работу / перезайти\n"
            "/order — оформить текущую корзину\n"
            "/my_orders — история заказов\n"
            "/cancel_order — отменить последний активный заказ\n"
            "/cancel — отменить текущее действие\n"
        )
    else:
        text = (
            "🛒 <b>Покупатель:</b>\n"
            "/start — начать работу / перезайти\n"
            "/order — оформить текущую корзину\n"
            "/my_orders — история заказов\n"
            "/cancel_order — отменить последний активный заказ\n"
            "/cancel — отменить текущее действие\n"
        )
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "/cancel")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Действие отменено.", reply_markup=get_main_menu())


@router.callback_query(F.data == "view_cart")
async def view_cart(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cart = data.get("cart", [])
    if not cart:
        await callback.answer("🛒 Корзина пуста.", show_alert=True)
        return
    total = sum(item["total_price"] for item in cart)
    items = "\n".join([f"• {item['berry']}: {item['kg']} кг" for item in cart])
    text = f"🧺 Корзина:\n{items}\n\n💰 Итого: {round(total, 2)}₽"
    await callback.answer(text, show_alert=True)