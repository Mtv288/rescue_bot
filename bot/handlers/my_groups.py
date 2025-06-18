from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot.database.base import Session
from bot.database.models import Group, Task, User
from bot.states import AssignGroup

router = Router()

@router.message(F.text == "/мои группы")
async def show_my_groups(message: Message):
    session = Session()
    user = session.query(User).filter_by(tg_id=message.from_user.id).first()
    if not user or user.role not in ["snm", "spg"]:
        await message.answer("Эта команда доступна только СНМ и СПГ")
        session.close()
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
        session.close()
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

@router.callback_query(F.data == "add_group")
async def add_group_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Введите название новой группы:")
    await state.set_state(AssignGroup.group_name)
    await callback.answer()

@router.message(AssignGroup.group_name)
async def process_group_name(message: Message, state: FSMContext):
    group_name = message.text.strip()
    if not group_name:
        await message.answer("Название группы не может быть пустым. Попробуйте снова.")
        return
    await state.update_data(group_name=group_name)
    await message.answer("Введите ID или позывной пользователя, которого хотите назначить лидером группы:")
    await state.set_state(AssignGroup.leader_id)

@router.message(AssignGroup.leader_id)
async def process_group_leader(message: Message, state: FSMContext):
    leader_input = message.text.strip()
    session = Session()

    user = None
    if leader_input.isdigit():
        user = session.query(User).filter_by(id=int(leader_input)).first()
    if not user:
        user = session.query(User).filter_by(call_sign=leader_input).first()

    if not user:
        await message.answer("Пользователь не найден. Попробуйте снова ввести ID или позывной:")
        session.close()
        return

    data = await state.get_data()
    group_name = data.get("group_name")

    # Проверяем, есть ли уже группа с таким названием у этого лидера
    existing_group = session.query(Group).filter_by(name=group_name, leader_id=user.id).first()
    if existing_group:
        await message.answer(f"Группа с названием '{group_name}' уже существует у лидера {user.call_sign}.")
        session.close()
        return

    # Создаем новую группу
    new_group = Group(name=group_name, leader_id=user.id)
    session.add(new_group)
    session.commit()

    leader_call_sign = user.call_sign
    session.close()

    await message.answer(f"✅ Группа '{group_name}' успешно создана с лидером {leader_call_sign}!")
    await state.clear()
