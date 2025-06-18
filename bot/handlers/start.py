from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot.keyboards.inline_buttons import start_menu_keyboard, main_menu_keyboard, admin_menu_keyboard
from bot.states import Registration
from bot.database.base import Session
from bot.database.models import User

router = Router()


# Обработчик команды /start — показываем стартовое меню с inline кнопками
@router.message(Command("start"))
async def start_handler(message: Message):
    session = Session()
    user = session.query(User).filter_by(tg_id=message.from_user.id).first()

    if not user:
        # Если не зарегистрирован — покажи кнопки "Войти" и "Зарегистрироваться"
        await message.answer(
            "👋 Привет! Добро пожаловать в бот спасателей.\n\n"
            "Пожалуйста, выберите действие:",
            reply_markup=start_menu_keyboard()
        )
    elif not user.approved:
        await message.answer("⏳ Ваша заявка на регистрацию ещё не одобрена.")
    else:
        # Если пользователь одобрен — сразу покажи нужное меню по роли
        if user.role == "admin":
            await message.answer(
                f"👤 Привет, {user.call_sign}! Это админ-меню:",
                reply_markup=admin_menu_keyboard()
            )
        else:
            await message.answer(
                f"👤 Привет, {user.call_sign}! Вот ваше меню:",
                reply_markup=main_menu_keyboard(user.role)
            )
    session.close()

# Логика нажатия кнопки "Войти"
@router.callback_query(F.data == "login")
async def login_callback(callback: types.CallbackQuery):
    session = Session()
    user = session.query(User).filter_by(tg_id=callback.from_user.id).first()

    if not user:
        await callback.message.answer("❌ Вы не зарегистрированы. Нажмите «Зарегистрироваться».")
    elif not user.approved:
        await callback.message.answer("⏳ Ваша заявка на регистрацию ещё не одобрена.")
    else:
        if user.role == "admin":
            await callback.message.answer(
                f"👤 Привет, {user.call_sign}! Это админ-меню:",
                reply_markup=admin_menu_keyboard()
            )
        else:
            await callback.message.answer(
                f"👤 Привет, {user.call_sign}! Вот ваше меню:",
                reply_markup=main_menu_keyboard(user.role)
            )
    session.close()
    await callback.answer()

# Логика нажатия кнопки "Зарегистрироваться"
@router.callback_query(F.data == "register")
async def register_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("✍️ Давайте зарегистрируем вас. Введите ваше имя:")
    await state.set_state(Registration.name)
    await callback.answer()
