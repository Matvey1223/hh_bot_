from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, reply_keyboard_remove
from keyboards import inline_keyboard, keyboards
from database import requests1 as db
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database.database import async_session
from models.models import Users, FilterLogs
from sqlalchemy import select, update



router = Router()
choosed_filters = []
class FrequenceVacancy(StatesGroup):
    hours = State()

class FreqeunceViews(StatesGroup):
    hours = State()

class ChangeFilter(StatesGroup):
    filter = State()
    option_to_change = State()
    salary = State()
    city = State()
    schedule = State()
    experience = State()
    test = State()


@router.callback_query(F.data == 'Настройки пользователя')
async def user_options_response(callback: CallbackQuery):
    text = '⚙️ Настройки\n' \
           'Ты находишься в разделе настроек, где можешь контролировать, как работает бот для тебя. Что бы ты хотел настроить сегодня?' \
           '\n1️⃣Изменить частоту уведомлений вакансий — настрой, как часто ты хочешь получать информацию о новых возможностях.' \
           '\n2️⃣Изменить критерии фильтрации поиска вакансий — измени параметры поиска, чтобы уведомления были максимально релевантными.' \
           '\n3️⃣Изменить частоту уведомлений просмотров резюме — выбери, как часто ты хочешь получать обновления о заинтересованности работодателей в твоём резюме. ' \
           '\n4️⃣Включить/Выключить уведомления о новых вакансиях — реши, хочешь ли ты получать уведомления о новых вакансиях.'
    await callback.message.answer(text = text,
                                  reply_markup=inline_keyboard.create_inline_kb(1, 'Частота уведомлений вакансий',
                                                                                'Вкл/выкл уведомления вакансий',
                                                                                'Фильтры уведомлений',
                                                                                'Частота просмотров резюме',
                                                                                'Изменить настройки фильтров',
                                                                                'Вернуться в главное меню'))

@router.callback_query(F.data == 'Частота уведомлений вакансий', StateFilter(None))
async def freq_vacancy_notifications(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        result = await session.execute(select(Users.new_vacancies_notification).where(Users.id == callback.from_user.id))
        result = result.fetchone()
    if result[0] == False:
        await callback.message.answer('🚫Уведомления на вакансии ещё не были включены!')
    else:
        await callback.message.answer('Как часто вы хотели бы получать уведомления?\n\nПожалуйста, '
                                      'напишите мне количество часов, через которое вы бы предпочли получать обновления. Например, если вы хотите получать уведомления каждый день, напишите 24. Для двух раз в день укажите 12 '
                                      'часов, и так далее. Это поможет настроить уведомления таким образом, чтобы они были максимально удобны именно для вас.')
        await state.set_state(FrequenceVacancy.hours)

@router.message(F.text, FrequenceVacancy.hours)
async def vacancy_freq_hours(message: Message, state: FSMContext):
    if int(message.text) >= 24:
        await message.answer('Нельзя устанавливать интервал больше <b>24 часов</b<')
    else:
        async with async_session() as session:
            await session.execute(update(Users).where(Users.id == message.from_user.id).values(
                freq_new_vacancy_notifications=int(message.text)))
            await session.commit()
        await message.answer(f'Вы измениили частоту уведомлений вакансий на {message.text} часов(а)')
        await state.clear()

@router.callback_query(F.data == 'Вкл/выкл уведомления вакансий')
async def off_on_vacancy_notifications(callback: CallbackQuery):
    async with async_session() as session:
        filters_with_true = await session.execute(select(FilterLogs.for_notifications).where(FilterLogs.for_notifications == True).where(FilterLogs.user_id == callback.from_user.id))
        filters_with_true = filters_with_true.fetchall()
    if filters_with_true:
        async with async_session() as session:
            result = await session.execute(select(Users.new_vacancies_notification).where(Users.id == callback.from_user.id))
            result = result.fetchone()
            if result[0] == False:
                await session.execute(update(Users).where(Users.id == callback.from_user.id).values(new_vacancies_notification = True))
                await session.commit()
                await callback.message.answer('✅ Теперь вы будете получать уведомления на новые вакансии!')
            else:
                await session.execute(update(Users).where(Users.id == callback.from_user.id).values(new_vacancies_notification = False))
                await session.commit()
                await callback.message.answer('🚫 Уведомления на новые вакансии были отключены!')
    else:
        await callback.message.answer('У вас не настроены никакие фильтры для уведомлений')


@router.callback_query(F.data == 'Фильтры уведомлений')
async def filter_notifications(callback: CallbackQuery):
    await callback.message.answer('Опции', reply_markup=inline_keyboard.create_inline_kb(2, 'Очистить фильтры', 'Изменить фильтры'))

@router.callback_query(F.data == 'Изменить фильтры')
async def change_filters_notifications(callback: CallbackQuery):
    if_filters = await db.manage_filter_logs(callback.from_user.id, True)
    print(if_filters)
    c = 1
    async with async_session() as session:
        count_true_filters = await session.execute(select(FilterLogs.user_id).where(FilterLogs.user_id == callback.from_user.id).where(FilterLogs.for_notifications == True))
        count_true_filters = count_true_filters.fetchall()
    if len(count_true_filters) == 3:
        await callback.message.answer('У вас уже есть 3 заполненных фильтра. Чтобы их изменить вам нужно очистить фильтры для уведомлений.')
    else:
        async with async_session() as session:
            if not if_filters:
                await callback.message.answer('🚫 Вы ещё не настроили фильтры для получения новых вакансий! Перейдите в меню «поиск вакансий». (это также для кнопки где изменяем критерии фильтрации поиска вакансий /включение уведомлях на вакансии)')
            else:
                for i in if_filters:
                    is_true_notifications = await session.execute(select(FilterLogs.for_notifications).where(FilterLogs.user_id == callback.from_user.id))
                    is_true_notifications = is_true_notifications.fetchone()
                    if is_true_notifications[0] == False:
                        await callback.message.answer(text=f'<b>{c}</b>\nЗапрос: {i[0]}\nЗарплата: {i[1]}\nГород: {i[2]}\nГрафик: {i[3]}\nОпыт: {i[4]}\nНаличие теста: {i[5]}\nПрофессиональные роли: {i[6]}')
                        c += 1
        await callback.message.answer('Вы можете добавить не более 3 фильтров по которым будут искаться вакансии для уведомлений.\n'
                                      'По завершении ввода нажмите кнопку завершить', reply_markup=inline_keyboard.create_inline_kb(1, *[str(i+1) for i in range(len(if_filters))], 'Завершить'))

@router.callback_query(F.data == 'Очистить фильтры')
async def clear_filters_notifications(callback: CallbackQuery):
    async with async_session() as session:
        await session.execute(update(FilterLogs).where(FilterLogs.user_id == callback.from_user.id).values(for_notifications = False))
        await session.commit()
    await callback.message.answer('Вы очистили все фильтры для уведомлений')

@router.callback_query(F.data.in_(['1','2','3','4','5', 'Завершить']))
async def select_filters_to_notifications(callback: CallbackQuery):
    global choosed_filters
    if callback.data in ['1','2','3','4','5']:
        choosed_filters.append(callback.data)
        print(choosed_filters)
    if len(choosed_filters) == 3:
        await callback.message.delete()
        await callback.message.answer('Вы обновили фильтры для уведомления вакансий')
        for i in choosed_filters:
            async with async_session() as session:
                filter_id = int(i)
                filter = await session.execute(select(FilterLogs.created_at).where(FilterLogs.user_id == callback.from_user.id).order_by(FilterLogs.created_at))
                filter = filter.fetchall()
                filter = filter[filter_id - 1]
                await session.execute(update(FilterLogs).where(FilterLogs.user_id == callback.from_user.id).where(FilterLogs.created_at == filter[-1]).values(for_notifications = True))
                await session.commit()
        await callback.bot.delete_message(chat_id = callback.from_user.id, message_id=callback.message.message_id - 1)
        await callback.bot.delete_message(chat_id = callback.from_user.id, message_id=callback.message.message_id - 2)
        await callback.bot.delete_message(chat_id = callback.from_user.id, message_id=callback.message.message_id - 3)
        await callback.bot.delete_message(chat_id = callback.from_user.id, message_id=callback.message.message_id - 4)
        await callback.bot.delete_message(chat_id = callback.from_user.id, message_id=callback.message.message_id - 5)
        await callback.bot.delete_message(chat_id = callback.from_user.id, message_id=callback.message.message_id - 6)
        choosed_filters = []
    if callback.data == 'Завершить':
        await callback.message.delete()
        await callback.message.answer('Вы обновили фильтры для уведомления вакансий')
        for i in choosed_filters:
            print(i)
            async with async_session() as session:
                filter_id = int(i)
                filter = await session.execute(select(FilterLogs.created_at).where(FilterLogs.user_id == callback.from_user.id).order_by(FilterLogs.created_at))
                filter = filter.fetchall()
                filter = filter[filter_id - 1]
                await session.execute(update(FilterLogs).where(FilterLogs.user_id == callback.from_user.id).where(FilterLogs.created_at == filter[-1]).values(for_notifications = True))
                await session.commit()
        await callback.bot.delete_message(chat_id = callback.from_user.id, message_id=callback.message.message_id - 1)
        await callback.bot.delete_message(chat_id = callback.from_user.id, message_id=callback.message.message_id - 2)
        await callback.bot.delete_message(chat_id = callback.from_user.id, message_id=callback.message.message_id - 3)
        await callback.bot.delete_message(chat_id = callback.from_user.id, message_id=callback.message.message_id - 4)
        await callback.bot.delete_message(chat_id = callback.from_user.id, message_id=callback.message.message_id - 5)
        await callback.bot.delete_message(chat_id = callback.from_user.id, message_id=callback.message.message_id - 6)
        choosed_filters = []

@router.callback_query(F.data == 'Изменить настройки фильтров', StateFilter(None))
async def change_filter_options(callback: CallbackQuery, state: FSMContext):
    if_filters = await db.manage_filter_logs(callback.from_user.id, True)
    c = 1
    if not if_filters:
        await callback.message.answer('У вас нет заполненный фильтров')
    else:
        for i in if_filters:
            await callback.message.answer(text=f'<b>{c}</b>\nЗапрос: {i[0]}\nЗарплата: {i[1]}\nГород: {i[2]}\nГрафик: {i[3]}\nОпыт: {i[4]}\nНаличие теста: {"True" if i[5] == False else "False"}\nПрофессиональные роли: {i[6]}',
                                          reply_markup=inline_keyboard.create_inline_kb(2, 'Изменить', 'Отменить действие'))
            c += 1
    await state.set_state(ChangeFilter.filter)

@router.callback_query(F.data.in_(['Изменить', 'Отменить действие']), ChangeFilter.filter)
async def change_salary(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'Изменить':
        await state.update_data(filter_number = callback.message.text[0])
        await callback.message.answer('Что бы вы хотели изменить?',
                                      reply_markup=inline_keyboard.create_inline_kb(2, 'Изменить зарплату', 'Изменить город', 'Изменить график', 'Изменить опыт', 'Изменить наличие теста'))
        await state.set_state(ChangeFilter.option_to_change)
    if callback.data == 'Отменить действие':
        await state.clear()

@router.callback_query(F.data.in_(['Изменить зарплату', 'Изменить город', 'Изменить график', 'Изменить опыт', 'Изменить наличие теста']), ChangeFilter.option_to_change)
async def change_option(callback: CallbackQuery, state: FSMContext):
    await state.update_data(option_to_change = callback.data)
    if callback.data == 'Изменить зарплату':
        await callback.message.answer('Введите желаемую зарплату в формате 30000-50000 или выберите из списка',
                                  reply_markup=keyboards.create_standard_kb(2, 'от 50 000 р', 'от 70 000 р', 'от 100 000 р', 'от 200 000 р'))
        await state.set_state(ChangeFilter.salary)
    if callback.data == 'Изменить город':
        await callback.message.answer('Введите желаемый город.')
        await state.set_state(ChangeFilter.city)
    if callback.data == 'Изменить график':
        await callback.message.answer('Выберите желаемый график', reply_markup=keyboards.create_standard_kb(2, 'Полный день', 'Удаленная работа', 'Гибкий график', 'Сменный график', 'Вахтовый метод'))
        await state.set_state(ChangeFilter.schedule)
    if callback.data == 'Изменить опыт':
        await callback.message.answer('Выберите желаемый график', reply_markup=keyboards.create_standard_kb(2, 'Нет опыта', 'От 1 года до 3 лет', 'От 3 до 6 лет', 'Более 6 лет'))
        await state.set_state(ChangeFilter.experience)
    if callback.data == 'Изменить наличие теста':
        await callback.message.answer('Выберите критерий наличия теста', reply_markup=keyboards.create_standard_kb(2, 'Да', 'Нет'))
        await state.set_state(ChangeFilter.test)

@router.message(F.text, StateFilter(*[ChangeFilter.salary, ChangeFilter.city, ChangeFilter.schedule, ChangeFilter.experience, ChangeFilter.test]))
async def change_choosed_option(message: Message, state: FSMContext):
    if await state.get_state() == ChangeFilter.salary:
        filters = await db.manage_filter_logs(message.from_user.id, True)
        id = await state.get_data()
        filters = filters[int(id['filter_number']) - 1]
        if '_' not in message.text:
            async with async_session() as session:
                await session.execute(update(FilterLogs).values(salary = message.text.split(' ')[1] + message.text.split(' ')[2]).
                                      where(FilterLogs.text == filters[0], FilterLogs.salary == filters[1], FilterLogs.city == filters[2],
                                            FilterLogs.schedule == filters[3], FilterLogs.experience == filters[4], FilterLogs.test == filters[5]))
                await session.commit()
        else:
            async with async_session() as session:
                await session.execute(update(FilterLogs).values(salary = message.text.split('-')[0]).
                                      where(FilterLogs.text == filters[0], FilterLogs.salary == filters[1], FilterLogs.city == filters[2],
                                            FilterLogs.schedule == filters[3], FilterLogs.experience == filters[4], FilterLogs.test == filters[5]))
                await session.commit()
        await message.answer(f'Вы изменили критерий зарплаты на {message.text}', reply_markup=reply_keyboard_remove.ReplyKeyboardRemove())
        await state.clear()
    if await state.get_state() == ChangeFilter.city:
        filters = await db.manage_filter_logs(message.from_user.id, True)
        id = await state.get_data()
        filters = filters[int(id['filter_number']) - 1]
        async with async_session() as session:
            await session.execute(
                update(FilterLogs).values(city=message.text).
                where(FilterLogs.text == filters[0], FilterLogs.salary == filters[1], FilterLogs.city == filters[2],
                      FilterLogs.schedule == filters[3], FilterLogs.experience == filters[4],
                      FilterLogs.test == filters[5]))
            await session.commit()
        await message.answer(f'Вы изменили город на {message.text}', reply_markup=reply_keyboard_remove.ReplyKeyboardRemove())
        await state.clear()
    if await state.get_state() == ChangeFilter.schedule:
        filters = await db.manage_filter_logs(message.from_user.id, True)
        id = await state.get_data()
        filters = filters[int(id['filter_number']) - 1]
        async with async_session() as session:
            await session.execute(
                update(FilterLogs).values(schedule=message.text).
                where(FilterLogs.text == filters[0], FilterLogs.salary == filters[1], FilterLogs.city == filters[2],
                      FilterLogs.schedule == filters[3], FilterLogs.experience == filters[4],
                      FilterLogs.test == filters[5]))
            await session.commit()
        await message.answer(f'Вы изменили график на {message.text}', reply_markup=reply_keyboard_remove.ReplyKeyboardRemove())
        await state.clear()
    if await state.get_state() == ChangeFilter.experience:
        filters = await db.manage_filter_logs(message.from_user.id, True)
        id = await state.get_data()
        filters = filters[int(id['filter_number']) - 1]
        async with async_session() as session:
            await session.execute(
                update(FilterLogs).values(experience=message.text).
                where(FilterLogs.text == filters[0], FilterLogs.salary == filters[1], FilterLogs.city == filters[2],
                      FilterLogs.schedule == filters[3], FilterLogs.experience == filters[4],
                      FilterLogs.test == filters[5]))
            await session.commit()
        await message.answer(f'Вы изменили критерий опыта на {message.text}', reply_markup=reply_keyboard_remove.ReplyKeyboardRemove())
        await state.clear()
    if await state.get_state() == ChangeFilter.test:
        if message.text == 'Да':
            filters = await db.manage_filter_logs(message.from_user.id, True)
            id = await state.get_data()
            filters = filters[int(id['filter_number']) - 1]
            async with async_session() as session:
                await session.execute(
                    update(FilterLogs).values(test=True).where(FilterLogs.text == filters[0], FilterLogs.salary == filters[1], FilterLogs.city == filters[2],
                          FilterLogs.schedule == filters[3], FilterLogs.experience == filters[4],
                          FilterLogs.test == filters[5]))
                await session.commit()
            await message.answer(f'Вы изменили критерий наличия теста на {message.text}', reply_markup=reply_keyboard_remove.ReplyKeyboardRemove())
            await state.clear()
        if message.text == 'Нет':
            filters = await db.manage_filter_logs(message.from_user.id, True)
            id = await state.get_data()
            filters = filters[int(id['filter_number']) - 1]
            async with async_session() as session:
                await session.execute(
                    update(FilterLogs).values(test=False).where(FilterLogs.text == filters[0], FilterLogs.salary == filters[1], FilterLogs.city == filters[2],
                          FilterLogs.schedule == filters[3], FilterLogs.experience == filters[4],
                          FilterLogs.test == filters[5]))
                await session.commit()
            await message.answer(f'Вы изменили критерий наличия теста на {message.text}', reply_markup=reply_keyboard_remove.ReplyKeyboardRemove())
            await state.clear()


@router.callback_query(F.data == 'Частота просмотров резюме', StateFilter(None))
async def freq_monitoring_resumes_request(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Как часто вы хотели бы получать уведомления?\n\nПожалуйста, '
                                  'напишите мне количество часов, через которое вы бы предпочли получать обновления. Например, если вы хотите получать уведомления каждый день, напишите 24. Для двух раз в день укажите 12 '
                                  'часов, и так далее. Это поможет настроить уведомления таким образом, чтобы они были максимально удобны именно для вас.')
    await state.set_state(FreqeunceViews.hours)


@router.message(F.text, FreqeunceViews.hours)
async def freq_monitoring_resumes_get(message: Message, state: FSMContext):
    if int(message.text) >= 24:
        await message.answer('Нельзя устанавливать интервал больше <b>24 часов</b>. Введите еще раз.')
    else:
        async with async_session() as session:
            await session.execute(update(Users).values(monitoring_resume_interval=int(message.text)).where(
                Users.id == message.from_user.id))
            await session.commit()
        await message.answer(f'Вы обновили частоту уведомлений о просмотрах резюме на {message.text}')
    await state.clear()









