from pkgutil import get_data

from aiogram import Router,F
from aiogram.handlers import CallbackQueryHandler
from pyexpat.errors import messages
from sqlalchemy.ext.asyncio import AsyncSession
from states.admin_state import AdminState
from keyboards.menu import admin_menu
from aiogram.types import CallbackQuery,Message
from aiogram.fsm.context import FSMContext
from db.requests import add_lesson,get_lessons

rt = Router()
@rt.callback_query(F.data == "admin_panel")
async def admin_panel(callback:CallbackQuery,state:FSMContext,session:AsyncSession):
    await callback.message.answer("Панель админа:",reply_markup= admin_menu())
@rt.callback_query(F.data == "admin_add_lesson")
async def callback_admin_add_lesson(callback:CallbackQuery,state:FSMContext,session:AsyncSession):
    await state.set_state(AdminState.add_lesson)
    await callback.message.answer("Введите название предмета:")
@rt.message(AdminState.add_lesson)
async def admin_add_lesson(message:Message,state:FSMContext,session:AsyncSession):
        await state.update_data(data=message.text)
        name_lesson = await state.get_data()
        await add_lesson(session,name_lesson['data'])
        await message.answer(f"Урок {name_lesson['data']} успешно добавлен!")
        await state.clear()