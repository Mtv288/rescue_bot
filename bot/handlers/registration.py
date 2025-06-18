from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline_buttons import main_menu_keyboard
from bot.states import Registration
from bot.database.base import Session
from bot.database.models import User

router = Router()

# Главное меню для одобренных пользователей
def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Задания"), KeyboardButton(text="📍 Место сбора")],
            [KeyboardButton(text="ℹ️ Профиль"), KeyboardButton(text="🔧 Настройки")]
        ],
        resize_keyboard=True
    )

@router.message(F.text == "📋 Меню")
async def show_main_menu(message: Message):
    session = Session()
    user = session.query(User).filter_by(tg_id=message.from_user.id).first()
    session.close()

    if not user:
        return await message.answer("❌ Вы не зарегистрированы. Пожалуйста, зарегистрируйтесь.")

    await message.answer(
        text=f"👋 Привет, {user.call_sign}! Вот ваше меню:",
        reply_markup=main_menu_keyboard(user.role)
    )

# Старт регистрации
@router.message(Command("register"))
async def register_start(message: Message, state: FSMContext):
    session = Session()
    existing = session.query(User).filter_by(tg_id=message.from_user.id).first()
    session.close()
    if existing:
        await message.answer("❗ Вы уже зарегистрированы или ожидаете подтверждения.")
        return

    await message.answer("📝 Введите ваше имя:")
    await state.set_state(Registration.name)

# Шаг 1: имя
@router.message(Registration.name, F.text)
async def register_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("🔤 Введите ваш позывной:")
    await state.set_state(Registration.call_sign)

# Шаг 2: позывной
@router.message(Registration.call_sign, F.text)
async def register_call_sign(message: Message, state: FSMContext):
    await state.update_data(call_sign=message.text.strip())
    await message.answer("📅 Введите ваш год рождения (например, 1990):")
    await state.set_state(Registration.birth_year)

# Шаг 3: год рождения
@router.message(Registration.birth_year, F.text)
async def register_birth_year(message: Message, state: FSMContext):
    try:
        birth_year = int(message.text.strip())
        if birth_year < 1900 or birth_year > 2025:
            raise ValueError()
    except ValueError:
        return await message.answer("❗ Введите корректный год рождения (например, 1995).")

    await state.update_data(birth_year=birth_year)
    data = await state.get_data()

    session = Session()
    existing = session.query(User).filter_by(tg_id=message.from_user.id).first()
    if existing:
        await message.answer("❗ Вы уже зарегистрированы или ожидаете подтверждения.")
        session.close()
        await state.clear()
        return

    user = User(
        tg_id=message.from_user.id,
        name=data["name"],
        call_sign=data["call_sign"],
        birth_year=data["birth_year"],
        approved=False,
        role="pending"
    )
    session.add(user)
    session.commit()
    session.close()

    await message.answer("✅ Спасибо! Ваша заявка отправлена на рассмотрение. ⏳")
    await state.clear()
