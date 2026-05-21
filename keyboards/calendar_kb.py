import calendar
from datetime import datetime,date
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_calendar(year:int|None=None,month:int|None=None):
    now=datetime.now()
    year=year or now.year
    month=month or now.month
    keyboards=[]
    keyboards.append([
        InlineKeyboardButton(text="◀️",callback_data=f"cal_prev.{year}.{month}"),
        InlineKeyboardButton(text=f"{calendar.month_name[month]} {year}",callback_data="ignore"),
        InlineKeyboardButton(text="▶️",callback_data=f"cal_next.{year}.{month}")
    ])
    weekdays=["Пн","Вт","Ср","Чт","Пт","Сб","Вс"]
    keyboards.append([InlineKeyboardButton(text=day,callback_data="ignore")for day in weekdays])

    for week in calendar.monthcalendar(year,month):
        row=[]
        for day_num in week:
            if day_num==0:
                row.append(InlineKeyboardButton(text=" ",callback_data="ignore"))
            else:
                result=date(year,month,day_num)
                if result<date.today():
                    row.append(InlineKeyboardButton(text=str(day_num),callback_data="ignore"))
                else:
                    row.append(InlineKeyboardButton(text=str(day_num),callback_data=f"cal_day.{year}.{month}.{day_num}"))

        keyboards.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboards)
