import asyncio
import logging
import os
from handlers.admin import rt as admin_router
from os import environ
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from db.database import engine, Base
from db import models
from handlers.booking import router as booking_router
from handlers.start import router as start_router
from middlewares.db import DbSessionMiddleware

load_dotenv()
TOKEN =os.getenv('BOT_TOKEN')
dp = Dispatcher()
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
# Run the bot
async def main() -> None:
    await create_tables()
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=TOKEN)
    dp.update.middleware(DbSessionMiddleware())
    dp.include_router(start_router)
    dp.include_router(booking_router)
    dp.include_router(admin_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
