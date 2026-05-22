from aiogram import Router,F
from aiogram.types import CallbackQuery,Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from states.admin_state import AdminState
from keyboards.menu import admin_menu,main_menu
from db.requests import add_lesson,get_lessons
from db.models import User,Lesson,Record

rt = Router()

@rt.callback_query(F.data == "admin_panel")
async def admin_panel(callback:CallbackQuery,state:FSMContext,session:AsyncSession):
    await callback.message.answer("Панель админа:",reply_markup=admin_menu())

@rt.callback_query(F.data == "admin_add_lesson")
async def callback_admin_add_lesson(callback:CallbackQuery,state:FSMContext,session:AsyncSession):
    await state.set_state(AdminState.add_lesson)
    await callback.message.answer("Введите название предмета:")

@rt.message(AdminState.add_lesson)
async def admin_add_lesson(message:Message,state:FSMContext,session:AsyncSession):
    await state.update_data({"data":message.text})
    name_lesson = await state.get_data()
    await add_lesson(session,name_lesson['data'])
    await message.answer(f"Урок {name_lesson['data']} успешно добавлен!")
    await state.clear()

@rt.callback_query(F.data == "admin_lessons")
async def callback_admin_lessons(callback:CallbackQuery,state:FSMContext,session:AsyncSession):
    lessons = await get_lessons(session)
    if not lessons:
        text = "Предметы отсутствуют"
    else:
        text = "Список предметов:"
        for lesson in lessons:
            text += f"ID: {lesson.id} | {lesson.name}"
    await callback.message.answer(text)
    await callback.message.answer("Панель админа:",reply_markup=admin_menu())

@rt.callback_query(F.data == "admin_users")
async def callback_admin_users(callback:CallbackQuery,state:FSMContext,session:AsyncSession):
    result = await session.execute(select(User))
    users = result.scalars().all()
    if not users:
        text = "Пользователи отсутствуют"
    else:
        text = "Список пользователей:"
        for user in users:
            text += f"ID: {user.id} | TG_ID: {user.tg_id} | Имя: {user.user_name} | Роль: {user.role}\n"
    await callback.message.answer(text)
    await callback.message.answer("Панель админа:",reply_markup=admin_menu())

@rt.callback_query(F.data == "admin_records")
async def callback_admin_records(callback:CallbackQuery,state:FSMContext,session:AsyncSession):
    result = await session.execute(select(Record).order_by(Record.date,Record.time))
    records = result.scalars().all()
    if not records:
        text = "Записи отсутствуют"
    else:
        text = "Все записи:"
        for rec in records:
            user_i = await session.execute(select(User).where(User.id==rec.user_id))
            user = user_i.scalar_one_or_none()
            lesson_i = await session.execute(select(Lesson).where(Lesson.id==rec.lesson_id))
            lesson = lesson_i.scalar_one_or_none()
            text += f"ID: {rec.id} | {user.user_name if user else '?'} | {lesson.name if lesson else '?'} | {rec.date} {rec.time}\n"
    await callback.message.answer(text)
    await callback.message.answer("Панель админа:",reply_markup=admin_menu())

@rt.callback_query(F.data == "back_main_menu")
async def callback_back_main_menu(callback:CallbackQuery,state:FSMContext,session:AsyncSession):
    result = await session.execute(select(User).where(User.tg_id==callback.from_user.id))
    user = result.scalar_one_or_none()
    is_admin = user.role == "admin" if user else False
    await callback.message.answer("Главное меню:",reply_markup=main_menu(is_admin=is_admin))
