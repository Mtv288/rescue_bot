from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot.database.base import Session
from bot.database.models import Group, Task, User

router = Router()

@router.message(F.text == "/моигруппы")
async def show_my_groups(message: Message):
    session = Session()
    user = session.query(User).filter_by(tg_id=message.from_user.id).first()
    if not user or user.role not in ["snm", "spg"]:
        await message.answer("Эта команда доступна только СНМ и СПГ")
        return

    groups = session.query(Group).filter_by(leader_id=user.id).all()
    if not groups:
        await message.answer("У вас нет групп")
    else:
        text = "📋 Ваши группы:\n"
        for group in groups:
            text += f"ID: {group.id} — {group.name}\n"
        await message.answer(text + "\nИспользуйте /задачи <ID> чтобы увидеть задачи")
    session.close()

@router.message(F.text.startswith("/задачи"))
async def show_group_tasks(message: Message):
    try:
        _, group_id = message.text.split()
        group_id = int(group_id)
    except:
        await message.answer("Используйте: /задачи <ID группы>")
        return

    session = Session()
    tasks = session.query(Task).filter_by(group_id=group_id).all()
    if not tasks:
        await message.answer("Нет задач для этой группы")
        return

    for task in tasks:
        status = "✅" if task.completed else "❗"
        markup = InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text="Завершить ✅", callback_data=f"complete:{task.id}")
            ]] if not task.completed else []
        )
        await message.answer(f"{status} Задача #{task.id}: {task.description}", reply_markup=markup)
    session.close()

@router.callback_query(F.data.startswith("complete:"))
async def complete_task_button(callback: CallbackQuery):
    task_id = int(callback.data.split(":")[1])
    session = Session()
    task = session.query(Task).filter_by(id=task_id).first()
    if task and not task.completed:
        task.completed = True
        session.commit()
        await callback.message.edit_text(f"✅ Задача #{task.id}: {task.description}\n(выполнена)")
    else:
        await callback.answer("Задача уже выполнена или не найдена")
    session.close()
