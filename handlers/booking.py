from datetime import date, datetime, time

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from db.requests import get_lessons, get_free_times, get_or_create_user, get_lesson_by_id, create_record
from keyboards.booking_kb import lessons_keyboard, times_keyboard
from keyboards.calendar_kb import get_calendar
from keyboards.menu import main_menu
from states.booking_state import BookingState

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
