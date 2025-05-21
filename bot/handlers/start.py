
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline_buttons import start_menu_keyboard, main_menu_keyboard, admin_menu_keyboard
from bot.states import Registration
from bot.database.base import Session
from bot.database.models import User

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    # При любом запуске /start показываем кнопки входа/регистрации
    await message.answer(
        "👋 Привет! Добро пожаловать в бот спасателей.\n\n"
        "Пожалуйста, выберите действие:",
        reply_markup=start_menu_keyboard()
    )

@router.callback_query(F.data == "login")
async def login_callback(callback: types.CallbackQuery):
    session = Session()
    user = session.query(User).filter_by(tg_id=callback.from_user.id).first()

    if not user:
        # Не зарегистрирован
        await callback.message.answer(
            "❌ Вы не зарегистрированы. Нажмите «Зарегистрироваться»."
        )
    elif not user.approved:
        # На рассмотрении
        await callback.message.answer(
            "⏳ Ваша заявка на регистрацию ещё не одобрена."
        )
    else:
        # Одобрен — показываем меню по роли
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

@router.callback_query(F.data == "register")
async def register_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "✍️ Давайте зарегистрируем вас. Введите ваше имя:"
    )
    await state.set_state(Registration.name)
    await callback.answer()

