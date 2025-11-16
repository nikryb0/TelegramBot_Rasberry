# handlers/start.py
import re
from aiogram import Router, F
from aiogram.types import Message, Contact, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, any_state


from config import ADMIN_ID
from keyboards.inline import get_main_menu
from storage.users import load_users, save_user

router = Router(name="start")


class RegistrationStates(StatesGroup):
    full_name = State()


@router.message(CommandStart(), StateFilter(any_state))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Здравствуйте! 👋\nЯ бот магазина «Ягодки».\n\n"
        "Пожалуйста, нажмите кнопку ниже, чтобы отправить ваш контакт и войти в аккаунт.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📲 Отправить контакт", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


@router.message(F.contact, StateFilter(any_state))
async def handle_contact(message: Message, state: FSMContext):
    print("📞 Контакт получен:", message.contact.phone_number)

    if not message.contact:
        await message.answer("Пожалуйста, используйте кнопку для отправки контакта.")
        return

    contact = message.contact

    # Проверка: контакт должен принадлежать отправителю
    if contact.user_id != message.from_user.id:
        await message.answer("❌ Пожалуйста, отправьте именно свой контакт.")
        return

    # Нормализация номера
    raw_phone = re.sub(r"\D", "", contact.phone_number)

    if len(raw_phone) == 11 and raw_phone.startswith(("7", "8")):
        phone = raw_phone[1:]
    elif len(raw_phone) == 10:
        phone = raw_phone
    else:
        await message.answer("❌ Некорректный номер телефона. Попробуйте снова.")
        return

    user_id = message.from_user.id
    users = load_users()

    if phone in users:
        # Вход
        user_data = users[phone]
        await state.update_data(
            user_id=user_id,
            phone=phone,
            full_name=user_data["full_name"]
        )
        await message.answer(
            f"👋 Добро пожаловать, {user_data['full_name']}!\n"
            f"📞 +7 {phone}\n\n"
            f"Вы вошли в свой аккаунт.",
            reply_markup=get_main_menu()
        )
    else:
        # Регистрация
        await state.update_data(user_id=user_id, phone=phone)
        await message.answer(
            "✅ Контакт сохранён!\n\n"
            "Теперь введите ваше ФИО (например: Иванов Иван Иванович):"
        )
        await state.set_state(RegistrationStates.full_name)


@router.message(RegistrationStates.full_name)
async def handle_full_name(message: Message, state: FSMContext):
    full_name = message.text.strip()

    # Валидация ФИО: три слова, кириллица, каждое с заглавной буквы
    if not re.fullmatch(r"[А-ЯЁ][а-яё]+ [А-ЯЁ][а-яё]+ [А-ЯЁ][а-яё]+", full_name):
        await message.answer(
            "❌ Пожалуйста, введите корректное ФИО из трёх слов (только кириллица, с заглавных букв).\n"
            "Пример: Иванов Иван Иванович"
        )
        return

    data = await state.get_data()
    phone = data["phone"]
    user_id = data["user_id"]

    # Сохраняем пользователя
    save_user(phone=phone, user_id=user_id, full_name=full_name)
    await state.update_data(full_name=full_name)

    await message.answer(
        f"🎉 Регистрация завершена, {full_name}!\n"
        f"📞 Ваш номер: +7 {phone}\n\n"
        f"Добро пожаловать в магазин «Ягодки»! 🍒",
        reply_markup=get_main_menu()
    )
    await state.set_state(None)