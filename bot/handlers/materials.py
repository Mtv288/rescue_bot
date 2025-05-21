from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.states import AddMaterial

router = Router()
materials = []

@router.message(Command("добавитьматериал"))
async def add_material(message: Message, state: FSMContext):
    await message.answer("Введите название материала:")
    await state.set_state(AddMaterial.title)

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
    text = "📚 Полезные материалы:\n" + "\n".join(f"- <a href='{url}'>{title}</a>" for title, url in materials)
    await message.answer(text)
