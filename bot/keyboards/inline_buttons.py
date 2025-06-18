from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def start_menu_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔑 Войти", callback_data="login"),
            InlineKeyboardButton(text="✍️ Зарегистрироваться", callback_data="register")
        ]
    ])
    return kb


def main_menu_keyboard(role: str) -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text='📍 Отправить геолокацию', callback_data='send_location')],
        [InlineKeyboardButton(text='📖 Полезные материалы', callback_data='materials')],
    ]
    if role in ['admin', 'chief']:
        kb.append([InlineKeyboardButton(text='➕ Добавить материал', callback_data='add_material')])
        kb.append([InlineKeyboardButton(text='➕ Добавить задачу', callback_data='create_task')])
        kb.append([InlineKeyboardButton(text='➕ Создать группу', callback_data='add_group')])

        kb.append([InlineKeyboardButton(text='📖 Добавить полезные материалы', callback_data='add_url_material')])
    return InlineKeyboardMarkup(inline_keyboard=kb)


def confirm_cancel_keyboard(confirm_cb: str, cancel_cb: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=confirm_cb),
            InlineKeyboardButton(text="❌ Отменить", callback_data=cancel_cb)
        ]
    ])


def group_selection_keyboard(groups: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, callback_data=f"choose_group:{group_id}")]
        for group_id, name in groups
    ])


def back_to_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_main")]
    ])


def admin_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📌 Задать задачу", callback_data="create_task")],
        [InlineKeyboardButton(text="📋 Заявки на регистрацию", callback_data="view_requests")],
        [InlineKeyboardButton(text="👤 Пользователи", callback_data="show_users")],
        [InlineKeyboardButton(text="🛠 Настройки", callback_data="admin_settings")]
    ])


def pending_user_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_user:{user_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_user:{user_id}")
        ]
    ])

InlineKeyboardButton(text="Пользователи", callback_data="show_users")
