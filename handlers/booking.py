from datetime import date, datetime, time

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery,Message
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from db.requests import get_lessons, get_free_times, get_or_create_user, get_lesson_by_id, create_record
from keyboards.booking_kb import lessons_keyboard, times_keyboard
from keyboards.calendar_kb import get_calendar
from keyboards.menu import main_menu
from states.booking_state import BookingState
from sqlalchemy import select
from db.models import Record

router=Router()
@router.callback_query(F.data=="start_booking")
async def start_booking(callback:CallbackQuery,state:FSMContext,session:AsyncSession):
    lessons=await get_lessons(session)
    if not lessons:
        await callback.message.answer("Нет доступных предметов")
        await callback.answer()
        return
    await state.clear()
    await state.set_state(BookingState.choosing_lesson)
    await callback.message.answer("Выберите предмет:",reply_markup=lessons_keyboard(lessons))
    await callback.answer()
@router.callback_query(BookingState.choosing_lesson,F.data.startswith("lesson:"))
async def choose_lesson(callback:CallbackQuery,state:FSMContext):
    lesson_id=int(callback.data.split(":")[1])
    await state.update_data(lesson_id=lesson_id)
    await state.set_state(BookingState.choosing_date)

    await callback.message.answer("Выберите дату:",reply_markup=get_calendar())

@router.callback_query(BookingState.choosing_date,F.data=="ignore")
async def ignore_calendar(callback:CallbackQuery,state:FSMContext):
    await callback.answer()

@router.callback_query(BookingState.choosing_date,F.data.startswith("cal_prev."))
async def prev_calendar(callback:CallbackQuery):
    _,year,month=callback.data.split(".")
    year=int(year)
    month=int(month)
    month-=1
    if month==0:
        month=12
        year-=1
    await callback.message.edit_reply_markup(reply_markup=get_calendar(year,month))
    await callback.answer()
@router.callback_query(BookingState.choosing_date,F.data.startswith("cal_next."))
async def next_calendar(callback:CallbackQuery):
    _,year,month=callback.data.split(".")
    year=int(year)
    month=int(month)
    month+=1
    if month==13:
        month=1
        year+=1
    await callback.message.edit_reply_markup(reply_markup=get_calendar(year,month))
    await callback.answer()
@router.callback_query(BookingState.choosing_date,F.data.startswith("cal_day."))
async def choose_date(callback:CallbackQuery,state:FSMContext,session:AsyncSession):
    _, year, month,day = callback.data.split(".")
    selected_date=date(int(year),int(month),int(day))


    if selected_date<date.today():
        await callback.message.answer("Нельзя выбрать прошедшую дату")
        return
    data=await state.get_data()
    lesson_id=data["lesson_id"]
    free_times=await get_free_times(session,lesson_id,selected_date)
    if not free_times:
        await callback.answer("На эту дату нет свободного времени", show_alert=True)
        return
    await  state.update_data(selected_date=selected_date.isoformat())
    await state.set_state(BookingState.choosing_time)
    await callback.message.answer(f"Дата: {selected_date.strftime('%d.%m.%Y')}\n Выберите время:",
                                  reply_markup=times_keyboard(free_times),)
    await callback.answer()
@router.callback_query(BookingState.choosing_time,F.data=="back_to_calendar")
async def back_to_calendar(callback:CallbackQuery,state:FSMContext):
    await state.set_state(BookingState.choosing_date)
    await callback.message.answer("Выберите дату:",reply_markup=get_calendar())
    await callback.answer()

@router.callback_query(BookingState.choosing_time,F.data.startswith("time:"))
async def choose_time(callback:CallbackQuery,state:FSMContext,session:AsyncSession):
    _,hour,minute=callback.data.split(":")
    selected_time=time(int(hour),int(minute))
    data=await state.get_data()
    lesson_id=data["lesson_id"]
    selected_data=date.fromisoformat(data["selected_date"])
    user=await get_or_create_user(
        session=session,
        tg_id=callback.from_user.id,
        user_name=callback.from_user.username or callback.from_user.full_name
    )
    lesson=await get_lesson_by_id(session,lesson_id)
    await create_record(
        session=session,
        user_id=user.id,
        lesson_id=lesson_id,
        selected_date=selected_data,
        selected_time=selected_time
    )
    await callback.answer()
    await callback.message.answer(
        f"Вы записаны на занятие:\n"
        f"Предмет: {lesson.name}\n"
        f"Дата: {selected_data.strftime('%d.%m.%Y')}\n"
        f"Время: {selected_time.strftime('%H:%M')}\n",reply_markup=main_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "my_records")
async def my_records(callback: CallbackQuery, session: AsyncSession):
    user = await get_or_create_user(session, tg_id=callback.from_user.id, user_name=callback.from_user.username or callback.from_user.full_name)
    brn = select(Record).where(Record.user_id == user.id).order_by(Record.date, Record.time)
    a = await session.execute(brn)
    b = a.scalars().all()
    if not b:
        text = "У вас нет записей lol"
    else:
        lines = ["Ваши записи:"]
        for rec in b:
            lesson = await get_lesson_by_id(session, rec.lesson_id)
            lines.append(f"{lesson.name} - {rec.date.strftime('%d.%m.%Y')} в {rec.time.strftime('%H:%M')}")
        linej = "\n".join(lines)
    await callback.message.answer(linej, reply_markup=main_menu())
    await callback.answer()

@router.callback_query(F.data == "cancel_record_menu")
async def cancel_record_menu(callback: CallbackQuery, session: AsyncSession):
    user_cn = await get_or_create_user(session, tg_id=callback.from_user.id, user_name=callback.from_user.username or callback.from_user.full_name)
    ffbd = select(Record).where(Record.user_id == user_cn.id).order_by(Record.date, Record.time)
    c = await session.execute(ffbd)
    d = c.scalars().all()
    if not d:
        await callback.message.answer("У вас нет записей1", reply_markup=main_menu())
        await callback.answer()
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{ (await get_lesson_by_id(session, rec.lesson_id)).name } {rec.date.strftime('%d.%m.%Y')} {rec.time.strftime('%H:%M')}", callback_data=f"cancel_{rec.id}")]
        for rec in d])
    await callback.message.answer("Выберите запись для отмены", reply_markup=keyboard)
    await callback.answer()
@router.callback_query(F.data.startswith("cancel_"))
async def cancel_record(callback: CallbackQuery, session: AsyncSession):
    #пу пу пу пу
    record_id = int(callback.data.split("_")[1])
    user = await get_or_create_user(session, tg_id=callback.from_user.id, user_name=callback.from_user.username or callback.from_user.full_name)
    g = (await session.execute(select(Record).where(Record.id == record_id, Record.user_id == user.id))).scalar_one_or_none()
    if g:
        await session.delete(g)
        await session.commit()
        await callback.answer()
        await callback.message.answer("Запись отменена", reply_markup=main_menu())
    else:
        await callback.answer("Запись не найдена", show_alert=True)
        
        
        
        
        
        
        
        
        
        
