import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import BOT_TOKEN
from bot.handlers import (
    start,
    registration,
    location,
    materials,
    admin,
    groups,
    stats,
    my_groups,
    admin_requests,
)

async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(registration.router)
    dp.include_router(location.router)
    dp.include_router(materials.router)
    dp.include_router(admin.router)
    dp.include_router(groups.router)
    dp.include_router(stats.router)
    dp.include_router(my_groups.router)
    dp.include_router(admin_requests.router)  # ✅ добавлено

    from bot.database.base import Base, engine
    Base.metadata.create_all(bind=engine)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
