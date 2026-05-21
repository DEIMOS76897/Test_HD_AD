from datetime import time, date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User, Lesson, Record


async def get_or_create_user(session: AsyncSession,tg_id:int,user_name:str):
    result=await session.execute(select(User).where(User.tg_id==tg_id))
    user=result.scalar_one_or_none()
    if not user:
        user = User(tg_id=tg_id,user_name=user_name)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user
async def make_admin(session: AsyncSession,tg_id:int,admin_id:int):
    result=await session.execute(select(User).where(User.tg_id==tg_id))
    user = result.scalar_one_or_none()
    if user and tg_id==admin_id and user.role!="admin":
        user.role="admin"
        await session.commit()
    else:
        user.role="user"
        await session.commit()

async def get_lessons(session: AsyncSession):
    result=await session.execute(select(Lesson).order_by(Lesson.id))
    return result.scalars().all()

async def add_lesson(session: AsyncSession,name_lesson:str):
    lesson=Lesson(name=name_lesson)
    session.add(lesson)
    await session.commit()
    await session.refresh(lesson)

async def get_lesson_by_id(session: AsyncSession,lesson_id:int):
    result=await session.execute(select(Lesson).where(Lesson.id==lesson_id))
    return result.scalar_one_or_none()

def generate_time_slots():
    slots=[]
    for i in range(9,21):
        slots.append(time(i,0))
        slots.append(time(i,30))
    return slots

async def get_busy_times(session: AsyncSession,lesson_id:int,selected_date:date):
    result=await session.execute(select(Record.time).where(Record.lesson_id==lesson_id,
                                                           Record.date==selected_date))
    return result.scalars().all()

async def get_free_times(session: AsyncSession,lesson_id:int,selected_date:date):
    now=datetime.now()
    all_times=generate_time_slots()
    busy_times=await get_busy_times(session,lesson_id,selected_date)
    free_times=[t for t in all_times if t not in busy_times]
    if selected_date == date.today():
        cur_time=now.time().replace(second=0,microsecond=0)
        free_times=[t for t in all_times if t>cur_time]
    return free_times

async def create_record(session: AsyncSession,
                        user_id:int,
                        lesson_id:int,
                        selected_date:date,
                        selected_time:time):
    record=Record(
        user_id=user_id,
        lesson_id=lesson_id,
        date=selected_date,
        time=selected_time)
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record