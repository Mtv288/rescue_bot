from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states import AddMaterial

router = Router()
materials = []

@router.callback_query(F.data == "add_material")
async def add_material_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название материала:")
    await state.set_state(AddMaterial.title)
    await callback.answer()

@router.message(AddMaterial.title)
async def get_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите URL:")
    await state.set_state(AddMaterial.url)

@router.message(AddMaterial.url)
async def save_material(message: Message, state: FSMContext):
    data = await state.get_data()
    materials.append((data["title"], message.text))
    await message.answer("Материал добавлен.")
    await state.clear()

@router.message(Command("материалы"))
async def show_materials(message: Message):
    if not materials:
        await message.answer("Материалов пока нет.")
        return
    text = "📚 Полезные материалы:\n" + "\n".join(
        f"- <a href='{url}'>{title}</a>" for title, url in materials
    )
    await message.answer(text, parse_mode="HTML", disable_web_page_preview=False)


@router.callback_query(F.data == "add_url_material")
async def ask_direct_url(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Отправьте ссылку на материал:")
    await state.set_state(AddMaterial.direct_url)
    await callback.answer()

@router.message(AddMaterial.direct_url)
async def save_direct_url(message: Message, state: FSMContext):
    url = message.text.strip()
    if not url.startswith("http"):
        await message.answer("Пожалуйста, отправьте корректную ссылку (начинается с http).")
        return
    materials.append((url, url))  # Название и ссылка одинаковы
    await message.answer("✅ Ссылка добавлена в материалы.")
    await state.clear()

@router.callback_query(F.data == "materials")
async def show_materials_callback(callback: CallbackQuery):
    if not materials:
        await callback.message.answer("Материалов пока нет.")
        await callback.answer()  # просто закрываем "часики"
        return
    text = "📚 Полезные материалы:\n" + "\n".join(
        f"- <a href='{url}'>{title}</a>" for title, url in materials
    )
    await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=False)
    await callback.answer()