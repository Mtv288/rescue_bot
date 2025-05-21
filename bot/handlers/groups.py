from aiogram import Router, F, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.states import AssignTask
from bot.database.base import Session
from bot.database.models import User, Group, Task

router = Router()

# 📌 Меню задач
@router.message(F.text == "/задачи")
async def show_task_menu(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📌 Задать задачу", callback_data="create_task")],
        [InlineKeyboardButton(text="👥 Просмотр заявок", callback_data="view_pending_users")]
    ])
    await message.answer("Меню задач и заявок:", reply_markup=keyboard)

# 🚀 Начать создание задачи
@router.callback_query(F.data == "create_task")
async def select_group(callback: CallbackQuery, state: FSMContext):
    session = Session()
    admin = session.query(User).filter_by(tg_id=callback.from_user.id).first()
    groups = session.query(Group).filter(
        (Group.leader_id == admin.id) |
        (admin.role == "шеф")
    ).all()
    session.close()

    if not groups:
        await callback.message.answer("Нет доступных групп.")
        await callback.answer()
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=group.name, callback_data=f"choose_group:{group.id}")]
        for group in groups
    ])
    await callback.message.edit_text("Выберите группу для назначения задачи:", reply_markup=keyboard)
    await callback.answer()

# 📝 Ввод описания задачи
@router.callback_query(F.data.startswith("choose_group:"))
async def input_task_description(callback: CallbackQuery, state: FSMContext):
    group_id = int(callback.data.split(":")[1])
    await state.update_data(group_id=group_id)
    await state.set_state(AssignTask.task)
    await callback.message.edit_text("Введите описание задачи:")
    await callback.answer()

# ✅ Сохранение задачи
@router.message(AssignTask.task)
async def save_task(message: Message, state: FSMContext):
    data = await state.get_data()
    session = Session()
    task = Task(group_id=data["group_id"], description=message.text)
    session.add(task)
    session.commit()
    group = session.query(Group).filter_by(id=data["group_id"]).first()
    await message.answer(f"✅ Задача успешно добавлена для группы: {group.name}")
    session.close()
    await state.clear()

# 📋 Просмотр заявок
@router.callback_query(F.data == "view_pending_users")
async def view_pending_users(callback: CallbackQuery):
    session = Session()
    pending = session.query(User).filter_by(approved=False).all()

    if not pending:
        await callback.message.answer("✅ Нет заявок на регистрацию.")
    else:
        for user in pending:
            buttons = [
                InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_user:{user.id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_user:{user.id}")
            ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
            await callback.message.answer(
                f"🆕 Заявка от:\n"
                f"ID: {user.id}\n"
                f"Позывной: {user.call_sign}\n"
                f"Tg ID: {user.tg_id}",
                reply_markup=keyboard
            )
    session.close()
    await callback.answer()

# ✅ Одобрение пользователя
@router.callback_query(F.data.startswith("approve_user:"))
async def approve_user_callback(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    session = Session()
    user = session.query(User).filter_by(id=user_id).first()

    if user:
        user.approved = True
        session.commit()
        await callback.message.edit_text(f"✅ Пользователь {user.call_sign} одобрен.")
    else:
        await callback.message.edit_text("❌ Пользователь не найден.")

    session.close()
    await callback.answer()

# ❌ Отклонение пользователя
@router.callback_query(F.data.startswith("reject_user:"))
async def reject_user_callback(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    session = Session()
    user = session.query(User).filter_by(id=user_id).first()

    if user:
        session.delete(user)
        session.commit()
        await callback.message.edit_text(f"🚫 Пользователь с ID {user_id} отклонён и удалён из базы.")
    else:
        await callback.message.edit_text("❌ Пользователь не найден.")

    session.close()
    await callback.answer()
