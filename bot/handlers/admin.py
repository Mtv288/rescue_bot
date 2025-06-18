from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
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

# ── Назначение роли через FSM ──
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

@router.message(AssignRole.role)
async def assign_set_role(message: Message, state: FSMContext):
    data = await state.get_data()
    session = Session()
    user = session.query(User).filter_by(id=data["user_id"]).first()
    if user:
        role = message.text.strip().lower()
        if role not in ("admin", "chief", "snm", "spg", "rescuer"):
            await message.answer("❌ Недопустимая роль. Попробуйте ещё раз.")
        else:
            user.role = role
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

    try:
        if user.role == "admin":
            keyboard = admin_menu_keyboard()
            text = f"👋 Привет, {user.call_sign}! Это ваше админ-меню:"
        else:
            keyboard = main_menu_keyboard(user.role)
            text = f"👋 Привет, {user.call_sign}! Добро пожаловать! Вот ваше меню:"
        await bot.send_message(chat_id=user.tg_id, text=text, reply_markup=keyboard)
    except Exception as e:
        await message.answer(f"⚠️ Не удалось отправить сообщение пользователю: {e}")

    session.close()

@router.callback_query(F.data == "show_users")
async def show_users_callback(callback: CallbackQuery):
    session = Session()
    users = session.query(User).all()
    session.close()

    if not users:
        return await callback.message.answer("❌ Пользователи не найдены.")

    buttons = []
    for u in users:
        text = f"{u.call_sign or 'Без позывного'} ({u.role or '—'})"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"select_user_{u.id}")])

    # Можно разбить на несколько сообщений, если пользователей очень много
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons[:40])  # максимум 100 кнопок на клавиатуре

    await callback.message.answer(
        "👥 Выберите пользователя для назначения роли:",
        reply_markup=keyboard
    )
    await callback.answer()

# ── Выбор пользователя из списка ──
@router.callback_query(F.data.startswith("select_user_"))
async def select_user_callback(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])
    roles = ["admin", "chief", "snm", "spg", "rescuer"]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=role, callback_data=f"assign_role_{user_id}_{role}")]
        for role in roles
    ])
    await callback.message.answer("🎯 Выберите новую роль для пользователя:", reply_markup=keyboard)
    await callback.answer()

# ── Назначение роли через кнопки ──
@router.callback_query(F.data.startswith("assign_role_"))
async def assign_role_callback(callback: CallbackQuery):
    _, _, user_id, role = callback.data.split("_")
    user_id = int(user_id)

    session = Session()
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        user.role = role
        session.commit()
        await callback.message.answer(f"✅ Пользователю {user.call_sign} назначена роль: {role}")
    else:
        await callback.message.answer("❌ Пользователь не найден.")
    session.close()
    await callback.answer()


@router.callback_query(F.data.startswith("reject_user:"))
async def reject_user_callback(callback: CallbackQuery, bot: Bot):
    user_id = int(callback.data.split(":")[1])

    session = Session()
    user = session.query(User).filter_by(id=user_id).first()

    if user:
        try:
            await bot.send_message(chat_id=user.tg_id, text="❌ Ваша заявка на регистрацию отклонена.")
        except Exception as e:
            await callback.message.answer(f"⚠️ Не удалось уведомить пользователя: {e}")

        session.delete(user)
        session.commit()
        await callback.message.answer(f"🚫 Заявка пользователя {user.call_sign} отклонена и удалена.")
    else:
        await callback.message.answer("❌ Пользователь не найден.")

    session.close()
    await callback.answer()

@router.message(Command("menu"))
async def show_menu(message: Message):
    session = Session()
    user = session.query(User).filter_by(tg_id=message.from_user.id).first()
    session.close()

    if not user:
        await message.answer("❌ Вы не зарегистрированы.")
        return

    await message.answer(
        f"📋 Главное меню для роли: {user.role}",
        reply_markup=main_menu_keyboard(user.role)
    )