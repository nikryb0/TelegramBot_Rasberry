# handlers/order.py
from datetime import datetime, timedelta
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import BERRIES, BERRY_PRICES, ADMIN_ID
from keyboards.reply import get_berry_keyboard
from keyboards.inline import get_date_keyboard, get_time_keyboard
from utils.helpers import extract_berry_name
from storage.orders import load_orders, save_orders, is_duplicate_order

router = Router(name="order")


class OrderStates(StatesGroup):
    select_berry = State()
    enter_quantity = State()
    choosing_date = State()
    choosing_time = State()


# === Начало заказа ===
@router.callback_query(F.data == "start_order")
async def start_order_process(callback: CallbackQuery, state: FSMContext):
    await state.update_data(cart=[])  # Сбрасываем корзину при новом заказе
    await state.set_state(OrderStates.select_berry)
    await callback.message.delete()  # удаляем старое меню
    await callback.message.answer("Давайте соберём ваш заказ.\nВыберите ягоду:", reply_markup=get_berry_keyboard())
    await callback.answer()


# === Выбор ягоды ===
@router.message(OrderStates.select_berry)
async def select_berry(message: Message, state: FSMContext):
    text = message.text.strip()

    # Если пользователь ввёл /order — выходим из FSM и обрабатываем
    if text == "/order":
        await state.set_state(None)
        return await cmd_order(message, state)

    if text == "Завершить заказ":
        return await confirm_cart(message, state)

    berry_name = extract_berry_name(text)
    if berry_name not in BERRY_PRICES:
        await message.answer("Пожалуйста, выберите ягоду из списка.")
        return await message.answer("Выберите ягоду:", reply_markup=get_berry_keyboard())

    await state.update_data(current_berry=berry_name)
    await message.answer(f"Сколько кг {berry_name.lower()} вы хотите заказать?")
    await state.set_state(OrderStates.enter_quantity)


# === Ввод количества ===
@router.message(OrderStates.enter_quantity)
async def enter_quantity(message: Message, state: FSMContext):
    text = message.text.strip()
    if text == "Завершить заказ":
        return await confirm_cart(message, state)

    try:
        quantity = float(text.replace(",", "."))
        if quantity <= 0 or quantity > 100:
            raise ValueError
    except ValueError:
        await message.answer("Пожалуйста, введите корректное количество (от 0.1 до 100 кг).")
        return

    data = await state.get_data()
    berry = data["current_berry"]
    price_per_kg = BERRY_PRICES[berry]
    total_price = round(price_per_kg * quantity, 2)

    cart = data.get("cart", [])
    cart.append({
        "berry": berry,
        "kg": quantity,
        "price_per_kg": price_per_kg,
        "total_price": total_price
    })
    await state.update_data(cart=cart)

    await message.answer(
        f"✅ {berry} ({quantity} кг × {price_per_kg}₽ = {total_price}₽) добавлено в заказ."
    )
    await state.set_state(OrderStates.select_berry)
    await message.answer("Выберите ещё ягоду или нажмите «Завершить заказ»:", reply_markup=get_berry_keyboard())


# === Подтверждение корзины ===
async def confirm_cart(message: Message, state: FSMContext):
    data = await state.get_data()
    cart = data.get("cart", [])
    if not cart:
        await message.answer("Ваша корзина пуста.")
        return

    items_text = ""
    total_sum = 0
    for item in cart:
        items_text += f"• {item['berry']}: {item['kg']} кг × {item['price_per_kg']}₽ = {item['total_price']}₽\n"
        total_sum += item['total_price']

    await message.answer(
        f"🧺 <b>Ваш заказ:</b>\n{items_text}\n"
        f"💰 <b>Итого: {round(total_sum, 2)}₽</b>\n\n"
        "Чтобы выбрать дату доставки, отправьте команду:\n/order",
        parse_mode="HTML"
    )


# === Команда /order — выбор даты ===
@router.message(F.text == "/order")
async def cmd_order(message: Message, state: FSMContext):
    data = await state.get_data()
    cart = data.get("cart", [])
    user_id = data.get("user_id")

    if not cart:
        await message.answer("Ваша корзина пуста. Сначала добавьте ягоды.")
        return
    if not user_id:
        await message.answer("Сначала войдите через /start.")
        return

    # Проверка на дубликат
    next_date = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
    if is_duplicate_order(cart, user_id, next_date):
        await message.answer(
            "⚠️ Вы уже оформляли идентичный заказ на ближайшую дату.\n"
            "Измените состав или подождите."
        )
        return

    # Генерация клавиатуры с датами
    today = datetime.now().date()
    keyboard = get_date_keyboard(today)
    await message.answer("📅 Выберите дату доставки:", reply_markup=keyboard)
    await state.set_state(OrderStates.choosing_date)


# === Выбор даты ===
@router.callback_query(F.data.startswith("date_"))
async def choose_date(callback: CallbackQuery, state: FSMContext):
    date_str = callback.data.split("_", 1)[1]
    await state.update_data(delivery_date=date_str)
    keyboard = get_time_keyboard()
    await callback.message.edit_text(f"🚚 Доставка {date_str}. Выберите удобное время:", reply_markup=keyboard)
    await state.set_state(OrderStates.choosing_time)
    await callback.answer()


# === Выбор времени и сохранение заказа ===
@router.callback_query(F.data.startswith("time_"))
async def choose_time(callback: CallbackQuery, state: FSMContext, bot: Bot):
    time_str = callback.data.split("_", 1)[1]
    await state.update_data(delivery_time=time_str)
    data = await state.get_data()

    # Загружаем и обновляем заказы
    orders_data = load_orders()
    order_id = orders_data["last_id"] + 1
    orders_data["last_id"] = order_id

    orders_data["orders"][str(order_id)] = {
        "user_id": data["user_id"],
        "full_name": data["full_name"],
        "phone": data["phone"],
        "cart": data["cart"],
        "date": data["delivery_date"],
        "time": data["delivery_time"],
        "status": "ожидает оплату"
    }
    save_orders(orders_data)

    # Считаем итог
    total = sum(item["total_price"] for item in data["cart"])
    cart_summary = "\n".join([f"• {item['berry']}: {item['kg']} кг" for item in data["cart"]])

    # Ответ пользователю
    await callback.message.edit_text(
        f"✅ Заказ №{order_id} успешно оформлен!\n"
        f"📅 {data['delivery_date']} в {data['delivery_time']}\n"
        f"💰 Итого: {round(total, 2)}₽\n\n"
        "Ожидайте ссылку на оплату от менеджера."
    )

    # Уведомление админу
    await bot.send_message(
        ADMIN_ID,
        f"🛒 <b>Новый заказ №{order_id}</b>\n"
        f"👤 {data['full_name']}\n"
        f"📞 +7{data['phone'][-10:]}\n"
        f"📅 {data['delivery_date']} в {data['delivery_time']}\n"
        f"📦\n{cart_summary}\n"
        f"💰 {round(total, 2)}₽\n\n"
        f"Используйте: /oplata {order_id} https://...",
        parse_mode="HTML"
    )

    await state.clear()
    await callback.answer()