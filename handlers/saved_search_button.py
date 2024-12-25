from aiogram import F, Router
from aiogram.types import CallbackQuery
from keyboards import inline_keyboard
from database import requests1 as db
from aiogram.fsm.context import FSMContext
from api.data_processor_api import SavedSearchFiltered
from ast import literal_eval


router = Router()
filtered_pages = 0
filtered_vacancies = []
def if_salary_none(item: str):
    item = literal_eval(item)
    if item == None:
        return 'Зарплата не указана'
    else:
        if item['from'] != None and item['to'] == None:
            return 'от ' + str(item['from']) + ' рублей'
        elif item['from'] == None and item['to'] != None:
            return 'до ' + str(item['to']) + ' рублей'
        elif item['from'] != None and item['to'] != None:
            return 'от ' + str(item['from']) + ' до ' + str(item['to']) + ' рублей'

@router.callback_query(F.data == 'Сохраненный поиск')
async def filter_logs(callback: CallbackQuery):
    global callback_ids
    if_filters = await db.manage_filter_logs(callback.from_user.id, True)
    c = 1
    if not if_filters:
        await callback.message.answer('У вас нет заполненный фильтров')
    else:
        for i in if_filters:
            await callback.message.answer(text=f'<b>{c}</b>\nЗапрос: {i[0]}\nЗарплата: {i[1]}\nГород: {i[2]}\nГрафик: {i[3]}\nОпыт: {i[4]}\nНаличие теста: {"True" if i[5] == False else "False"}\nПрофессиональные роли: {i[6]}',
                                          reply_markup=inline_keyboard.create_inline_kb(1, 'Посмотреть'))
            c += 1

@router.callback_query(F.data == 'Посмотреть')
async def saved_search_show(callback: CallbackQuery):
    global filtered_vacancies
    if callback.message.text[0] == '1':
        result = await db.all_vacancies(callback.from_user.id)
        filtered_vacancies = await SavedSearchFiltered(result, callback.from_user.id, callback.message.text[0]).filtered_by_salary()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filtered_by_area()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filtered_by_schedule()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filtered_by_experience()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filetered_by_test()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filetered_by_role()
        try:
            await callback.message.edit_text(
                text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                     f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}'
                     f'\n\n<b>{filtered_vacancies[filtered_pages + 2][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 2][1])}\n{filtered_vacancies[filtered_pages + 2][7]}\n\n'
                     f'<b>{filtered_vacancies[filtered_pages + 3][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 3][1])}\n{filtered_vacancies[filtered_pages + 3][7]}\n\n'
                     f'<b>{filtered_vacancies[filtered_pages + 4][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 4][1])}\n{filtered_vacancies[filtered_pages + 4][7]}',
                reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
        except IndexError:
            try:
                if len(filtered_vacancies) == 0:
                    await callback.message.edit_text('Найдено 0 вакансий',
                                                     reply_markup=inline_keyboard.create_inline_kb(1, 'Закрыть'))
                    filtered_vacancies = []
                if filtered_vacancies[filtered_pages + 0]:
                    await callback.message.edit_text(
                        text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}',
                        reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
                if filtered_vacancies[filtered_pages + 0] and filtered_vacancies[filtered_pages + 1]:
                    await callback.message.edit_text(
                        text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}',
                        reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
                if filtered_vacancies[filtered_pages + 0] and filtered_vacancies[filtered_pages + 1] and \
                        filtered_vacancies[filtered_pages + 2]:
                    await callback.message.edit_text(
                        text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 2][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 2][1])}\n{filtered_vacancies[filtered_pages + 2][7]}\n\n',
                        reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
                if filtered_vacancies[filtered_pages + 0] and filtered_vacancies[filtered_pages + 1] and \
                        filtered_vacancies[filtered_pages + 2] and filtered_vacancies[filtered_pages + 3]:
                    await callback.message.edit_text(
                        text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 2][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 2][1])}\n{filtered_vacancies[filtered_pages + 2][7]}\n\n'
                             f'<b>{filtered_vacancies[filtered_pages + 3][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 3][1])}\n{filtered_vacancies[filtered_pages + 3][7]}\n\n',
                        reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
            except IndexError:
                pass
        print([print(i) for i in filtered_vacancies])
    if callback.message.text[0] == '2':
        result = await db.all_vacancies(callback.from_user.id)
        filtered_vacancies = await SavedSearchFiltered(result, callback.from_user.id, callback.message.text[0]).filtered_by_salary()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filtered_by_area()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filtered_by_schedule()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filtered_by_experience()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filetered_by_test()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filetered_by_role()
        try:
            await callback.message.edit_text(
                text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                     f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}'
                     f'\n\n<b>{filtered_vacancies[filtered_pages + 2][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 2][1])}\n{filtered_vacancies[filtered_pages + 2][7]}\n\n'
                     f'<b>{filtered_vacancies[filtered_pages + 3][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 3][1])}\n{filtered_vacancies[filtered_pages + 3][7]}\n\n'
                     f'<b>{filtered_vacancies[filtered_pages + 4][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 4][1])}\n{filtered_vacancies[filtered_pages + 4][7]}',
                reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
        except IndexError:
            try:
                if len(filtered_vacancies) == 0:
                    await callback.message.edit_text('Найдено 0 вакансий',
                                                     reply_markup=inline_keyboard.create_inline_kb(1, 'Закрыть'))
                    filtered_vacancies = []
                if filtered_vacancies[filtered_pages + 0]:
                    await callback.message.edit_text(
                        text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}',
                        reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
                if filtered_vacancies[filtered_pages + 0] and filtered_vacancies[filtered_pages + 1]:
                    await callback.message.edit_text(
                        text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}',
                        reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
                if filtered_vacancies[filtered_pages + 0] and filtered_vacancies[filtered_pages + 1] and \
                        filtered_vacancies[filtered_pages + 2]:
                    await callback.message.edit_text(
                        text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 2][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 2][1])}\n{filtered_vacancies[filtered_pages + 2][7]}\n\n',
                        reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
                if filtered_vacancies[filtered_pages + 0] and filtered_vacancies[filtered_pages + 1] and \
                        filtered_vacancies[filtered_pages + 2] and filtered_vacancies[filtered_pages + 3]:
                    await callback.message.edit_text(
                        text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 2][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 2][1])}\n{filtered_vacancies[filtered_pages + 2][7]}\n\n'
                             f'<b>{filtered_vacancies[filtered_pages + 3][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 3][1])}\n{filtered_vacancies[filtered_pages + 3][7]}\n\n',
                        reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
            except IndexError:
                pass
    if callback.message.text[0] == '3':
        result = await db.all_vacancies(callback.from_user.id)
        filtered_vacancies = await SavedSearchFiltered(result, callback.from_user.id, callback.message.text[0]).filtered_by_salary()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filtered_by_area()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filtered_by_schedule()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filtered_by_experience()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filetered_by_test()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filetered_by_role()
        try:
            await callback.message.edit_text(
                text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                     f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}'
                     f'\n\n<b>{filtered_vacancies[filtered_pages + 2][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 2][1])}\n{filtered_vacancies[filtered_pages + 2][7]}\n\n'
                     f'<b>{filtered_vacancies[filtered_pages + 3][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 3][1])}\n{filtered_vacancies[filtered_pages + 3][7]}\n\n'
                     f'<b>{filtered_vacancies[filtered_pages + 4][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 4][1])}\n{filtered_vacancies[filtered_pages + 4][7]}',
                reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
        except IndexError:
            try:
                if len(filtered_vacancies) == 0:
                    await callback.message.edit_text('Найдено 0 вакансий',
                                                     reply_markup=inline_keyboard.create_inline_kb(1, 'Закрыть'))
                    filtered_vacancies = []
                if filtered_vacancies[filtered_pages + 0]:
                    await callback.message.edit_text(
                        text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}',
                        reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
                if filtered_vacancies[filtered_pages + 0] and filtered_vacancies[filtered_pages + 1]:
                    await callback.message.edit_text(
                        text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}',
                        reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
                if filtered_vacancies[filtered_pages + 0] and filtered_vacancies[filtered_pages + 1] and \
                        filtered_vacancies[filtered_pages + 2]:
                    await callback.message.edit_text(
                        text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 2][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 2][1])}\n{filtered_vacancies[filtered_pages + 2][7]}\n\n',
                        reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
                if filtered_vacancies[filtered_pages + 0] and filtered_vacancies[filtered_pages + 1] and \
                        filtered_vacancies[filtered_pages + 2] and filtered_vacancies[filtered_pages + 3]:
                    await callback.message.edit_text(
                        text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 2][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 2][1])}\n{filtered_vacancies[filtered_pages + 2][7]}\n\n'
                             f'<b>{filtered_vacancies[filtered_pages + 3][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 3][1])}\n{filtered_vacancies[filtered_pages + 3][7]}\n\n',
                        reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
            except IndexError:
                pass
    if callback.message.text[0] == '4':
        result = await db.all_vacancies(callback.from_user.id)
        filtered_vacancies = await SavedSearchFiltered(result, callback.from_user.id, callback.message.text[0]).filtered_by_salary()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filtered_by_area()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filtered_by_schedule()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filtered_by_experience()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filetered_by_test()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filetered_by_role()
        try:
            await callback.message.edit_text(
                text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                     f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}'
                     f'\n\n<b>{filtered_vacancies[filtered_pages + 2][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 2][1])}\n{filtered_vacancies[filtered_pages + 2][7]}\n\n'
                     f'<b>{filtered_vacancies[filtered_pages + 3][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 3][1])}\n{filtered_vacancies[filtered_pages + 3][7]}\n\n'
                     f'<b>{filtered_vacancies[filtered_pages + 4][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 4][1])}\n{filtered_vacancies[filtered_pages + 4][7]}',
                reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
        except IndexError:
            try:
                if len(filtered_vacancies) == 0:
                    await callback.message.edit_text('Найдено 0 вакансий',
                                                     reply_markup=inline_keyboard.create_inline_kb(1, 'Закрыть'))
                    filtered_vacancies = []
                if filtered_vacancies[filtered_pages + 0]:
                    await callback.message.edit_text(
                        text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}',
                        reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
                if filtered_vacancies[filtered_pages + 0] and filtered_vacancies[filtered_pages + 1]:
                    await callback.message.edit_text(
                        text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}',
                        reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
                if filtered_vacancies[filtered_pages + 0] and filtered_vacancies[filtered_pages + 1] and \
                        filtered_vacancies[filtered_pages + 2]:
                    await callback.message.edit_text(
                        text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 2][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 2][1])}\n{filtered_vacancies[filtered_pages + 2][7]}\n\n',
                        reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
                if filtered_vacancies[filtered_pages + 0] and filtered_vacancies[filtered_pages + 1] and \
                        filtered_vacancies[filtered_pages + 2] and filtered_vacancies[filtered_pages + 3]:
                    await callback.message.edit_text(
                        text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 2][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 2][1])}\n{filtered_vacancies[filtered_pages + 2][7]}\n\n'
                             f'<b>{filtered_vacancies[filtered_pages + 3][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 3][1])}\n{filtered_vacancies[filtered_pages + 3][7]}\n\n',
                        reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
            except IndexError:
                pass
    if callback.message.text[0] == '5':
        result = await db.all_vacancies(callback.from_user.id)
        filtered_vacancies = await SavedSearchFiltered(result, callback.from_user.id, callback.message.text[0]).filtered_by_salary()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filtered_by_area()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filtered_by_schedule()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filtered_by_experience()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filetered_by_test()
        filtered_vacancies = await SavedSearchFiltered(filtered_vacancies, callback.from_user.id, callback.message.text[0]).filetered_by_role()
        print(filtered_vacancies)
        try:
            await callback.message.edit_text(
                text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                     f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}'
                     f'\n\n<b>{filtered_vacancies[filtered_pages + 2][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 2][1])}\n{filtered_vacancies[filtered_pages + 2][7]}\n\n'
                     f'<b>{filtered_vacancies[filtered_pages + 3][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 3][1])}\n{filtered_vacancies[filtered_pages + 3][7]}\n\n'
                     f'<b>{filtered_vacancies[filtered_pages + 4][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 4][1])}\n{filtered_vacancies[filtered_pages + 4][7]}',
                reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
        except IndexError:
            try:
                if len(filtered_vacancies) == 0:
                    await callback.message.edit_text('Найдено 0 вакансий',
                                                     reply_markup=inline_keyboard.create_inline_kb(1, 'Закрыть'))
                    filtered_vacancies = []
                if filtered_vacancies[filtered_pages + 0]:
                    await callback.message.edit_text(
                        text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}',
                        reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
                if filtered_vacancies[filtered_pages + 0] and filtered_vacancies[filtered_pages + 1]:
                    await callback.message.edit_text(
                        text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}',
                        reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
                if filtered_vacancies[filtered_pages + 0] and filtered_vacancies[filtered_pages + 1] and \
                        filtered_vacancies[filtered_pages + 2]:
                    await callback.message.edit_text(
                        text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 2][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 2][1])}\n{filtered_vacancies[filtered_pages + 2][7]}\n\n',
                        reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
                if filtered_vacancies[filtered_pages + 0] and filtered_vacancies[filtered_pages + 1] and \
                        filtered_vacancies[filtered_pages + 2] and filtered_vacancies[filtered_pages + 3]:
                    await callback.message.edit_text(
                        text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 2][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 2][1])}\n{filtered_vacancies[filtered_pages + 2][7]}\n\n'
                             f'<b>{filtered_vacancies[filtered_pages + 3][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 3][1])}\n{filtered_vacancies[filtered_pages + 3][7]}\n\n',
                        reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
            except IndexError:
                pass

@router.callback_query(F.data.in_(['Дальше', 'Начало', 'Закрыть']))
async def look_filtered(callback: CallbackQuery, state: FSMContext):
    global filtered_vacancies, filtered_pages, result
    if callback.data == 'Дальше':
        filtered_pages += 5
        try:
            await callback.message.edit_text(
                text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                     f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}'
                     f'\n\n<b>{filtered_vacancies[filtered_pages + 2][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 2][1])}\n{filtered_vacancies[filtered_pages + 2][7]}\n\n'
                     f'<b>{filtered_vacancies[filtered_pages + 3][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 3][1])}\n{filtered_vacancies[filtered_pages + 3][7]}\n\n'
                     f'<b>{filtered_vacancies[filtered_pages + 4][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 4][1])}\n{filtered_vacancies[filtered_pages + 4][7]}',
                reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
        except IndexError:
            try:
                if filtered_vacancies[filtered_pages + 0] and filtered_vacancies[filtered_pages + 1] and \
                        filtered_vacancies[filtered_pages + 2] and filtered_vacancies[filtered_pages + 3]:
                    await callback.message.edit_text(
                        text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 2][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 2][1])}\n{filtered_vacancies[filtered_pages + 2][7]}\n\n'
                             f'<b>{filtered_vacancies[filtered_pages + 3][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 3][1])}\n{filtered_vacancies[filtered_pages + 3][7]}\n\n',
                        reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
            except IndexError:
                try:
                    if filtered_vacancies[filtered_pages + 0] and filtered_vacancies[filtered_pages + 1] and \
                            filtered_vacancies[filtered_pages + 2]:
                        await callback.message.edit_text(
                            text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                                 f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}'
                                 f'\n\n<b>{filtered_vacancies[filtered_pages + 2][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 2][1])}\n{filtered_vacancies[filtered_pages + 2][7]}\n\n',
                            reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
                except IndexError:
                    try:
                        if filtered_vacancies[filtered_pages + 0] and filtered_vacancies[filtered_pages + 1]:
                            await callback.message.edit_text(
                                text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                                     f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}',
                                reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
                    except IndexError:
                        if filtered_vacancies[filtered_pages + 0]:
                            await callback.message.edit_text(
                                text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}',
                                reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
    if callback.data == 'Начало':
        filtered_pages = 0
        try:
            await callback.message.edit_text(
                text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                     f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}'
                     f'\n\n<b>{filtered_vacancies[filtered_pages + 2][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 2][1])}\n{filtered_vacancies[filtered_pages + 2][7]}\n\n'
                     f'<b>{filtered_vacancies[filtered_pages + 3][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 3][1])}\n{filtered_vacancies[filtered_pages + 3][7]}\n\n'
                     f'<b>{filtered_vacancies[filtered_pages + 4][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 4][1])}\n{filtered_vacancies[filtered_pages + 4][7]}',
                reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
        except IndexError:
            try:
                if filtered_vacancies[filtered_pages + 0] and filtered_vacancies[filtered_pages + 1] and \
                        filtered_vacancies[filtered_pages + 2] and filtered_vacancies[filtered_pages + 3]:
                    await callback.message.edit_text(
                        text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}'
                             f'\n\n<b>{filtered_vacancies[filtered_pages + 2][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 2][1])}\n{filtered_vacancies[filtered_pages + 2][7]}\n\n'
                             f'<b>{filtered_vacancies[filtered_pages + 3][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 3][1])}\n{filtered_vacancies[filtered_pages + 3][7]}\n\n',
                        reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
            except IndexError:
                try:
                    if filtered_vacancies[filtered_pages + 0] and filtered_vacancies[filtered_pages + 1] and \
                            filtered_vacancies[filtered_pages + 2]:
                        await callback.message.edit_text(
                            text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                                 f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}'
                                 f'\n\n<b>{filtered_vacancies[filtered_pages + 2][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 2][1])}\n{filtered_vacancies[filtered_pages + 2][7]}\n\n',
                            reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
                except IndexError:
                    try:
                        if filtered_vacancies[filtered_pages + 0] and filtered_vacancies[filtered_pages + 1]:
                            await callback.message.edit_text(
                                text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                                     f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}',
                                reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
                    except IndexError:
                        if filtered_vacancies[filtered_pages + 0]:
                            await callback.message.edit_text(
                                text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}',
                                reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
    if callback.data == 'Закрыть':
        await callback.message.delete()
        filtered_vacancies = []
        filtered_pages = 0
