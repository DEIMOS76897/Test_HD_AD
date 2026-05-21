from aiogram.fsm.state import StatesGroup, State


class AdminState(StatesGroup):
    add_lesson = State()
    get_all_lessons = State()
    list_users = State()
    all_records = State()

