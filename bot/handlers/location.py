from aiogram import Router, F
from aiogram.types import Message, Location, ContentType

router = Router()

@router.message(F.content_type == ContentType.LOCATION)
async def save_location(message: Message):
    loc: Location = message.location
    await message.answer(f"📍 Геопозиция получена: {loc.latitude}, {loc.longitude}")

