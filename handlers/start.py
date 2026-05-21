import os

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

from db.requests import get_or_create_user, make_admin
from keyboards.menu import main_menu

load_dotenv()
ADMIN_ID=int(os.getenv('ADMIN_ID'))
router = Router()
@router.message(CommandStart())
async def command_start(message: Message,session:AsyncSession):
    await get_or_create_user(
        session=session,
        tg_id=message.from_user.id,
        user_name=message.from_user.username or message.from_user.full_name
    )
    await make_admin(session,message.from_user.id,ADMIN_ID)
    is_admin=message.from_user.id == ADMIN_ID
    await message.answer("Добро пожаловать в бот записи на занятия",
                         reply_markup=main_menu(is_admin=is_admin))