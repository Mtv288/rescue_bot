from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def menu_button_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📋 Меню")]],
        resize_keyboard=True,
        one_time_keyboard=False
    )
