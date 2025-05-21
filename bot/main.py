from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import (start, registration, location, materials,
                      admin, groups, stats, my_groups)

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

dp.include_routers(
    start.router,
    registration.router,
    location.router,
    materials.router,
    admin.router,
    groups.router,
    stats.router,
    my_groups.router
)

def main():
    import asyncio
    from database import Base, engine
    Base.metadata.create_all(bind=engine)
    asyncio.run(dp.start_polling(bot))

if __name__ == "__main__":
    main()
