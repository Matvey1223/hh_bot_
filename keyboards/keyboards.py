from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


# Функция для создания автоматической клавиатуры
def create_standard_kb(width: int,
                       *args: str,
                       **kwargs: str) -> ReplyKeyboardMarkup:

    # Инициализируем билдер
    kb_builder = ReplyKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[KeyboardButton] = []

    # Загружаем список кнопками из аргументов args и kwargs
    if args:
        for button in args:
            buttons.append(KeyboardButton(
                text=button,
                callback_data=button))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(KeyboardButton(
                text=text,
                callback_data=button))

    # Распаковываем список с кнопками в билдер методом row с параметром widht
    kb_builder.row(*buttons, width=width)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup(resize_keyboard=True)
