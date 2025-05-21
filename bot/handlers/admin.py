from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.states import AssignRole
from bot.database.base import Session
from bot.database.models import User
from bot.config import INITIAL_ADMIN_CODE
from bot.keyboards.inline_buttons import main_menu_keyboard, admin_menu_keyboard

router = Router()

# ── Команда для установки первого администратора ──
@router.message(Command("setup_admin"))
async def setup_admin(message: Message, command: Command):
    if not command.args:
        return await message.answer("❗ Используйте: /setup_admin <код>")

    code = command.args.strip()
    if code != INITIAL_ADMIN_CODE:
        return await message.answer("❌ Неверный код.")

    session = Session()
    user = session.query(User).filter_by(tg_id=message.from_user.id).first()
    if not user:
        user = User(
            tg_id=message.from_user.id,
            call_sign=message.from_user.username or str(message.from_user.id),
            role="admin",
            approved=True
        )
        session.add(user)
    else:
        user.role = "admin"
        user.approved = True

    session.commit()
    session.close()
    await message.answer("✅ Вы теперь администратор!")

# ── Назначение роли ──
@router.message(Command("назначить"))
async def assign_start(message: Message, state: FSMContext):
    session = Session()
    caller = session.query(User).filter_by(tg_id=message.from_user.id).first()
    session.close()
    if not caller or caller.role not in ("admin", "chief"):
        return await message.answer("⛔ У вас нет прав для назначения ролей.")

    await message.answer("Введите ID пользователя, которому хотите назначить роль:")
    await state.set_state(AssignRole.user_id)

@router.message(AssignRole.user_id, F.text.regexp(r"^\d+$"))
async def assign_get_user(message: Message, state: FSMContext):
    await state.update_data(user_id=int(message.text))
    await message.answer("Введите роль (admin, chief, snm, spg, rescuer):")
    await state.set_state(AssignRole.role)

@router.message(AssignRole.role, F.text)
async def assign_set_role(message: Message, state: FSMContext):
    data = await state.get_data()
    session = Session()
    user = session.query(User).filter_by(id=data["user_id"]).first()
    if user:
        new_role = message.text.strip().lower()
        if new_role not in ("admin", "chief", "snm", "spg", "rescuer"):
            await message.answer("❌ Недопустимая роль. Попробуйте ещё раз.")
        else:
            user.role = new_role
            session.commit()
            await message.answer(f"✅ Пользователю {user.call_sign} назначена роль: {user.role}")
    else:
        await message.answer("❌ Пользователь не найден.")
    session.close()
    await state.clear()

# ── Утверждение регистрации ──
@router.message(Command("утвердить"))
async def approve_user(message: Message, bot: Bot):
    session = Session()
    caller = session.query(User).filter_by(tg_id=message.from_user.id).first()

    if not caller or caller.role not in ("admin", "chief"):
        session.close()
        return await message.answer("⛔ У вас нет прав для утверждения заявок.")

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        session.close()
        return await message.answer("❗ Используйте: /утвердить <user_id>")

    user_id = int(parts[1])
    user = session.query(User).filter_by(id=user_id).first()

    if not user:
        session.close()
        return await message.answer("❌ Пользователь не найден.")

    user.approved = True
    session.commit()
    await message.answer(f"✅ Пользователь {user.call_sign} одобрен.")

    # Отправляем пользователю приветствие и клавиатуру
    try:
        if user.role == "admin":
            keyboard = admin_menu_keyboard()
            text = f"👋 Привет, {user.call_sign}! Это ваше админ-меню:"
        else:
            keyboard = main_menu_keyboard(user.role)
            text = f"👋 Привет, {user.call_sign}! Добро пожаловать! Вот ваше меню:"

        await bot.send_message(
            chat_id=user.tg_id,
            text=text,
            reply_markup=keyboard
        )
    except Exception as e:
        await message.answer(f"⚠️ Не удалось отправить сообщение пользователю: {e}")

    session.close()
