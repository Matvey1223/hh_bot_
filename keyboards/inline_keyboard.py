from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder




# Функция для создания автоматической клавиатуры
def create_inline_kb(width: int,
                     *args: str,
                     **kwargs: str) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []

    # Загружаем список кнопками из аргументов args и kwargs
    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(
                text=button,
                callback_data=button))
    kb_builder.row(*buttons, width=width)
    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


def city_kb(width: int, buttons: list[str]) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    inline_buttons: list[InlineKeyboardButton] = []

    # Создаем кнопки на основе переданного списка
    for button_text in buttons:
        inline_buttons.append(InlineKeyboardButton(text=button_text, callback_data=button_text))

    # Группируем кнопки в рядах с учетом ширины
    grouped_buttons = [inline_buttons[i:i+width] for i in range(0, len(inline_buttons), width)]

    # Добавляем ряды кнопок в клавиатуру
    for row_buttons in grouped_buttons:
        kb_builder.row(*row_buttons)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()

def work_with_resume(width: int,
                     args: list, datas: list) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []

    # Загружаем список кнопками из аргументов args и kwargs

    for i in range(len(args)):
        buttons.append(InlineKeyboardButton(text = args[i], callback_data=datas[i]))
    kb_builder.row(*buttons, width=width)
    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()