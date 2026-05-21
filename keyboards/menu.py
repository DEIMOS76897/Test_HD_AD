from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu(is_admin=False):
    keyboard=[
        [InlineKeyboardButton(text="Записаться",callback_data="start_booking")],
        [InlineKeyboardButton(text="Мои записи",callback_data="my_records")],
        [InlineKeyboardButton(text="Отменить запись",callback_data="cancel_record_menu")]

    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton(text="Админ-панель",callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить предмет", callback_data="admin_add_lesson")],
        [InlineKeyboardButton(text="Список предметов",callback_data="admin_lessons")],
        [InlineKeyboardButton(text="Список пользователей", callback_data="admin_users")],
        [InlineKeyboardButton(text="Все записи", callback_data="admin_records")],
        [InlineKeyboardButton(text="Назад",callback_data="back_main_menu")]
    ])