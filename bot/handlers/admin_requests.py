from aiogram import Router, F, types
from aiogram.types import CallbackQuery
from bot.keyboards.inline_buttons import pending_user_keyboard, admin_menu_keyboard
from bot.database.base import Session
from bot.database.models import User

router = Router()


# 👁 Показать список заявок
@router.callback_query(F.data == "view_requests")
async def view_pending_requests(callback: CallbackQuery):
    session = Session()
    pending_users = session.query(User).filter_by(approved=False).all()

    if not pending_users:
        await callback.message.edit_text("✅ Нет новых заявок на рассмотрение.", reply_markup=admin_menu_keyboard())
        session.close()
        return

    for user in pending_users:
        text = f"📌 Заявка от пользователя:\n\n" \
               f"🆔 ID: {user.id}\n" \
               f"👤 Позывной: {user.call_sign or '—'}\n" \
               f"🧾 Telegram ID: {user.tg_id}"
        await callback.message.answer(text, reply_markup=pending_user_keyboard(user.id))

    session.close()
    await callback.answer()


# ✅ Одобрить пользователя
@router.callback_query(F.data.startswith("approve_user:"))
async def approve_user(callback: CallbackQuery):
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


# ❌ Отклонить пользователя
@router.callback_query(F.data.startswith("reject_user:"))
async def reject_user(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    session = Session()
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        session.delete(user)
        session.commit()
        await callback.message.edit_text(f"❌ Заявка от {user.call_sign or 'пользователя'} удалена.")
    else:
        await callback.message.edit_text("❌ Пользователь не найден.")
    session.close()
    await callback.answer()
