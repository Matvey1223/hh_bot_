from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile, reply_keyboard_remove
from keyboards import inline_keyboard, keyboards
from database import requests1 as db
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from api.api import run
from api.data_processor_api import DataProcessor
from ast import literal_eval
from sqlalchemy import delete
from models.models import Users, UserResumes, UserVacancies, FilterLogs
from database.database import async_session

router = Router()
class AskVacancieText(StatesGroup):
    vacancie = State()

class Filters(StatesGroup):
    salary = State()
    city = State()
    city_keyboard = State()
    shedule = State()
    experience = State()
    test = State()
    prof_roles = State()
    show_filtered = State()
    show_more_filtered = State()

all_vacancies = None
city_pages = 0
all_cities = []
roles_pages = 0
all_prof_roles  = []
choosed_roles = []
filtered_vacancies = None
filtered_pages = 0
button_to_update = []

def if_salary_none(item: str):
    if item == 'None':
        return 'Зарплата не указана'
    else:
        item = literal_eval(item)
        if item['from'] != None and item['to'] == None:
            return 'от ' + str(item['from']) + ' рублей'
        elif item['from'] == None and item['to'] != None:
            return 'до ' + str(item['to']) + ' рублей'
        elif item['from'] != None and item['to'] != None:
            return 'от ' + str(item['from']) + ' до ' + str(item['to']) + ' рублей'

@router.message(CommandStart())
async def start(message: Message):
    await db.add_user(message.from_user.id, message.from_user.username)
    await message.answer('🤖Приветствую! Я твой помощник в поиске работы на HH.ru!🌟 🔍Что я умею?\n1) Поиск вакансий: Введи должность или ключевые слова, и я предложу тебе список подходящих вакансий, с возможностью перелистывания и получения детальной информации по каждой из них.'
                         '\n2) Аналитическая статистика: После каждого поиска ты получишь статистику по уровню зарплат, опыту работы, и другим важным показателям.'
                         '\n3) Управление резюме: Авторизуйся и я помогу тебе управлять твоими резюме, включая автообновление и мониторинг просмотров.'
                         '\n4) Персонализированные уведомления: Подпишись на уведомления, и я буду присылать тебе новые вакансии согласно твоим предпочтениям, их может быть несколько!'
                         '\n5) Настройки поиска: Настрой частоту уведомлений и критерии поиска вакансий, чтобы получать только самую релевантную информацию.'
                         '\n🎯Для чего я нужен?'
                         '\nМоя задача — сделать твой поиск работы максимально простым и эффективным. Я помогу тебе найти идеальное место и поддерживать твои резюме в актуальном состоянии.'
                         '\n\n📬Как начать работу со мной?'
                         '\nПросто выбери любую необходимую тебе кнопку для дальнейшей работы!'
                         '\nЖду твоих команд, чтобы помочь тебе в этом важном процессе поиска работы! ✨')
    await message.bot.send_photo(chat_id=message.from_user.id, photo=FSInputFile('static/hh.jpg'),
                                 caption='🌐Главное Меню\nВыбери интересующий тебя раздел, используя кнопки ниже:\n'
                                         '🔍 Поиск Вакансий - Начни поиск работы, указав желаемую должность или ключевые слова'
                                         '\n⚙️ Настройки - Настрой параметры поиска вакансий и частоту уведомлений.'
                                         '\n📄 Работа с Резюме - Управляй своими резюме, обновляй их, включай мониторинг просмотров.\n'
                                         '🚫 Забыть Меня - Удали всю свою информацию из базы данных бота.'
                                         '\n✉️ Обратная Связь - Отправь свои вопросы, предложения или отзывы создателю бота.'
                                         '\n🤖 Я здесь, чтобы помочь тебе найти идеальную работу.',
                                 reply_markup=inline_keyboard.create_inline_kb(2, 'Поиск вакансий', 'Работа с резюме', 'Настройки пользователя', 'Забыть меня', 'Обратная связь'))

@router.callback_query(F.data == 'Забыть меня')
async def forget_me(callback: CallbackQuery):
    async with async_session() as session:
        await session.execute(delete(Users).where(Users.id == callback.from_user.id))
        await session.commit()
        await session.execute(delete(UserResumes).where(UserResumes.user_id == callback.from_user.id))
        await session.commit()
        await session.execute(delete(UserVacancies).where(UserVacancies.user_id == callback.from_user.id))
        await session.commit()
        await session.execute(delete(FilterLogs).where(FilterLogs.user_id == callback.from_user.id))
        await session.commit()
    text = '✅ Все ваши данные удалены' \
           '\nМы удалили всю информацию, связанную с вашим аккаунтом. Теперь вы можете быть уверены, что ваша личная информация, история поиска вакансий, резюме, фильтры и настройки были полностью и безвозвратно удалены из нашей базы данных' \
           '\nБлагодарим вас за использование нашего сервиса, и помните, что вы всегда можете вернуться, если снова понадобится помощь в поиске работы.'
    await callback.message.answer(text = text)

@router.callback_query(F.data == 'Поиск вакансий', StateFilter(None))
async def ask_for_vacancie(callback: CallbackQuery, state: FSMContext):
    text = '🔎 Поиск вакансий' \
           '\nДавайте начнем поиск вашей идеальной работы! Пожалуйста, укажите область или специализацию, которая вас интересует. Это поможет нам найти самые подходящие вакансии специально для вас. Вы можете ввести название профессии ' \
           '\nПример: Если вы ищете работу в сфере программирования на Python, просто введите «Программист Python». Мы найдем для вас актуальные вакансии, соответствующие этому запросу. '
    await callback.message.answer(text = text)
    await state.set_state(AskVacancieText.vacancie)


@router.message(F.text, AskVacancieText.vacancie)
async def response(message: Message, state: FSMContext):
    await state.update_data(vacancie = message.text)
    data = await state.get_data()
    await db.add_user_text_api(str(message.from_user.id), data['vacancie'])
    text = '🔎 Ищем вакансии...' \
           '\nПожалуйста, подожди немного. Я собираю самые актуальные вакансии, которые соответствуют твоим критериям поиска. Это не займёт много времени! Твоя следующая работа уже где-то рядом, и мы её найдём!'
    msg = await message.answer(text = text)
    result = await run(data['vacancie'])
    await db.add_vacancies(message.from_user.id, result)
    text1 = '✅Сбор вакансий завершён!\n' \
            'Мы нашли ряд вакансий, которые могут быть интересны именно тебе. Что ты предпочитаешь сделать дальше?' \
            '\n1️⃣Показать Вакансии - Могу отобразить список найденных вакансий.' \
            '\n2️⃣Аналитическая Статистика - Могу предоставить аналитическую статистику по результатам поиска.' \
            '\n3️⃣Ввести Рекомендации - Можешь ввести дополнительные рекомендации, чтобы уточнить критерии поиска.'
    await message.bot.edit_message_text(text= text1,
                                        message_id=msg.message_id, chat_id=message.from_user.id,
                                        reply_markup=inline_keyboard.create_inline_kb(2, 'Вывести аналитику', 'Отобразить вакансии', 'Рекомендации поиска', 'Сохраненный поиск', 'Вернуться в главное меню'))
    await state.clear()


@router.callback_query(F.data == 'В меню')
async def to_menu(callback: CallbackQuery):
    text1 = '✅Сбор вакансий завершён!\n' \
            'Мы нашли ряд вакансий, которые могут быть интересны именно тебе. Что ты предпочитаешь сделать дальше?' \
            '\n1️⃣Показать Вакансии - Могу отобразить список найденных вакансий.' \
            '\n2️⃣Аналитическая Статистика - Могу предоставить аналитическую статистику по результатам поиска.' \
            '\n3️⃣Ввести Рекомендации - Можешь ввести дополнительные рекомендации, чтобы уточнить критерии поиска.'
    await callback.message.bot.edit_message_text(text= text1,
                                        message_id=callback.message.message_id, chat_id=callback.from_user.id,
                                        reply_markup=inline_keyboard.create_inline_kb(2, 'Вывести аналитику', 'Отобразить вакансии', 'Рекомендации поиска', 'Сохраненный поиск', 'Вернуться в главное меню'))



@router.callback_query(F.data == 'Рекомендации поиска', StateFilter(None))
async def start_filters(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите желаемую зарплату в формате 30000-50000 или выберите из списка',
                                  reply_markup=keyboards.create_standard_kb(2, 'от 50 000 р', 'от 70 000 р', 'от 100 000 р', 'от 200 000 р', 'Пропустить'))
    await state.set_state(Filters.salary)

@router.message(F.text, Filters.salary)
async def salary_input(message: Message, state: FSMContext):
    global all_cities, city_pages
    all_cities = await db.cities(message.from_user.id)
    if message.text == '/clear':
        await state.clear()
        await message.bot.send_photo(chat_id=message.from_user.id, photo=FSInputFile('static/hh.jpg'),
                                     caption='🌐Главное Меню\nВыбери интересующий тебя раздел, используя кнопки ниже:\n'
                                             '🔍 Поиск Вакансий - Начни поиск работы, указав желаемую должность или ключевые слова'
                                             '\n⚙️ Настройки - Настрой параметры поиска вакансий и частоту уведомлений.'
                                             '\n📄 Работа с Резюме - Управляй своими резюме, обновляй их, включай мониторинг просмотров.\n'
                                             '🚫 Забыть Меня - Удали всю свою информацию из базы данных бота.'
                                             '\n✉️ Обратная Связь - Отправь свои вопросы, предложения или отзывы создателю бота.'
                                             '\n🤖 Я здесь, чтобы помочь тебе найти идеальную работу.',
                                     reply_markup=inline_keyboard.create_inline_kb(2, 'Поиск вакансий',
                                                                                   'Работа с резюме',
                                                                                   'Настройки пользователя',
                                                                                   'Забыть меня', 'Обратная связь'))
    else:
        if '-' in message.text:
            await db.add_params(message.from_user.id, {'salary': message.text.split('-')[0]})
            await message.answer(f'Критерий зарплаты {message.text} добавлен', reply_markup=reply_keyboard_remove.ReplyKeyboardRemove())
            await message.answer('Выберите город в котором вы ищете работу либо введите вручную',
                                 reply_markup=inline_keyboard.create_inline_kb(2, all_cities[city_pages + 0],
                                                                               all_cities[city_pages + 1],
                                                                               all_cities[city_pages + 2],
                                                                               all_cities[city_pages + 3], 'Еще->',
                                                                               'Начало', 'Меню', 'Ввести вручную'))

            await state.set_state(Filters.city)
        else:
            await db.add_params(message.from_user.id, {'salary': message.text.split(' ')[1] + message.text.split(' ')[2]})
            await message.answer(f'Критерий зарплаты {message.text} добавлен', reply_markup=reply_keyboard_remove.ReplyKeyboardRemove())
            await message.answer('Выберите город в котором вы ищете работу либо введите вручную',
                                 reply_markup=inline_keyboard.create_inline_kb(2, all_cities[city_pages + 0], all_cities[city_pages + 1], all_cities[city_pages + 2], all_cities[city_pages + 3], 'Еще->', 'Начало', 'Меню', 'Ввести вручную'))
            await state.set_state(Filters.city)



@router.callback_query(F.data, Filters.city)
async def city_input(callback: CallbackQuery, state: FSMContext):
    global city_pages, all_cities
    if callback.data not in ['Еще->', 'Начало', 'Меню', 'Ввести вручную']:
        await db.add_params(callback.from_user.id, {'city': callback.data})
        await state.update_data(city = callback.data)
        await callback.message.answer('Выберите желаемый график работы',
                                      reply_markup=inline_keyboard.create_inline_kb(2, 'Полный день', 'Удаленная работа', 'Гибкий график', 'Сменный график', 'Вахтовый метод', 'Пропустить'))
        await state.set_state(Filters.shedule)
    if callback.data == 'Еще->':
        city_pages += 5
        try:
            await callback.message.edit_text('Выберите город в котором вы ищете работу',
                                          reply_markup=inline_keyboard.create_inline_kb(2, all_cities[city_pages + 0], all_cities[city_pages + 1], all_cities[city_pages + 2], all_cities[city_pages + 3], 'Еще->', 'Начало', 'Меню', 'Ввести вручную'))
        except IndexError:
            try:
                if all_cities[city_pages + 0]:
                    await callback.message.edit_text('Выберите город в котором вы ищете работу',
                                          reply_markup=inline_keyboard.create_inline_kb(2, all_cities[city_pages + 0], 'Еще->', 'Начало', 'Меню', 'Ввести вручную'))
                if all_cities[city_pages + 0] and all_cities[city_pages + 1]:
                    await callback.message.edit_text('Выберите город в котором вы ищете работу',
                                          reply_markup=inline_keyboard.create_inline_kb(2, all_cities[city_pages + 0], all_cities[city_pages + 1], 'Еще->', 'Начало', 'Меню', 'Ввести вручную'))
                if all_cities[city_pages + 0] and all_cities[city_pages + 1] and all_cities[city_pages + 2]:
                    await callback.message.edit_text('Выберите город в котором вы ищете работу',
                                          reply_markup=inline_keyboard.create_inline_kb(2, all_cities[city_pages + 0], all_cities[city_pages + 1], all_cities[city_pages + 2], 'Еще->', 'Начало', 'Меню', 'Ввести вручную'))
            except IndexError:
                pass
        await state.set_state(Filters.city)
    if callback.data == 'Начало':
        city_pages = 0
        await callback.message.edit_text('Выберите город в котором вы ищете работу',
                             reply_markup=inline_keyboard.create_inline_kb(2, all_cities[city_pages + 0], all_cities[city_pages + 1], all_cities[city_pages + 2], all_cities[city_pages + 3], 'Еще->', 'Начало', 'Меню', 'Ввести вручную'))
        await state.set_state(Filters.city)
    if callback.data == 'Ввести вручную':
        await state.set_state(Filters.city_keyboard)
    if callback.data == 'Меню':
        await callback.message.edit_text(
            text=f'<b>Сбор вакансий завершен. Найдено {str(len(result))} вакансий для Вас</b>\n\nХотите ли вы отобразить найденные вакансии или вывести аналитическую статистику по найденным вакансиям?',
            reply_markup=inline_keyboard.create_inline_kb(2, 'Вывести аналитику', 'Отобразить вакансии',
                                                          'Рекомендации поиска', 'Сохраненный поиск', 'Вернуться в главное меню'))
        await state.clear()


@router.message(F.text, Filters.city_keyboard)
async def city_keyboard_input(message: Message, state: FSMContext):
    await db.add_params(message.from_user.id, {'city': message.text})
    await message.answer('Выберите желаемый график работы',
                                  reply_markup=inline_keyboard.create_inline_kb(2, 'Полный день', 'Удаленная работа',
                                                                                'Гибкий график', 'Сменный график',
                                                                                'Вахтовый метод', 'Пропустить'))
    await state.set_state(Filters.shedule)


@router.callback_query(F.data, Filters.shedule)
async def schedule_input(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'Пропустить':
        await db.add_params(callback.from_user.id, {'shedule': callback.data})
        await callback.message.answer('Выберите опыт работы',
                                      reply_markup=inline_keyboard.create_inline_kb(2, 'От 1 года до 3 лет', 'От 3 до 6 лет', 'Более 6 лет', 'Нет опыта'))
        await state.set_state(Filters.experience)
    else:
        await db.add_params(callback.from_user.id, {'shedule': callback.data})
        await callback.message.answer('Выберите опыт работы',
                                      reply_markup=inline_keyboard.create_inline_kb(2, 'От 1 года до 3 лет', 'От 3 до 6 лет', 'Более 6 лет', 'Нет опыта'))
        await state.set_state(Filters.experience)

@router.callback_query(F.data, Filters.experience)
async def exp_input(callback: CallbackQuery, state: FSMContext):
    await db.add_params(callback.from_user.id, {'experience': callback.data})
    await callback.message.answer('Выберите наличие тестового задания', reply_markup=inline_keyboard.create_inline_kb(2, 'Да', 'Нет'))
    await state.set_state(Filters.test)

@router.callback_query(F.data, Filters.test)
async def test_input(callback: CallbackQuery, state: FSMContext):
    global filtered_vacancies, roles_pages, all_prof_roles, all_vacancies
    result = await db.all_vacancies(callback.from_user.id)
    if callback.data == 'Да':
        await db.add_params(callback.from_user.id, {'test': 'False'})
        filtered_vacancies = await DataProcessor(result, callback.from_user.id).filtered_by_salary()
        filtered_vacancies = await DataProcessor(filtered_vacancies, callback.from_user.id).filtered_by_area()
        filtered_vacancies = await DataProcessor(filtered_vacancies, callback.from_user.id).filtered_by_schedule()
        filtered_vacancies = await DataProcessor(filtered_vacancies, callback.from_user.id).filtered_by_experience()
        filtered_vacancies = await DataProcessor(filtered_vacancies, callback.from_user.id).filetered_by_test()
        all_prof_roles = await DataProcessor(filtered_vacancies, callback.from_user.id).all_prof_roles()
        try:
            await callback.message.answer('Выберите профессиональнуые роли',
                                      reply_markup=inline_keyboard.create_inline_kb(1, all_prof_roles[roles_pages + 0], all_prof_roles[roles_pages + 1], all_prof_roles[roles_pages + 2], all_prof_roles[roles_pages + 3], 'Далее', 'Закончить ввод', 'Пропустить'))
        except IndexError:
            try:
                if all_prof_roles[roles_pages + 0] and all_prof_roles[roles_pages + 1] and all_prof_roles[
                    roles_pages + 2]:
                    await callback.message.answer('Выберите профессиональнуые роли',
                                                  reply_markup=inline_keyboard.create_inline_kb(1, all_prof_roles[
                                                      roles_pages + 0], all_prof_roles[roles_pages + 1], all_prof_roles[
                                                                                                    roles_pages + 2],
                                                                                                'Далее',
                                                                                                'Закончить ввод',
                                                                                                'Пропустить'))
            except Exception:
                try:
                    if all_prof_roles[roles_pages + 0] and all_prof_roles[roles_pages + 1]:
                        await callback.message.answer('Выберите профессиональнуые роли',
                                                      reply_markup=inline_keyboard.create_inline_kb(1, all_prof_roles[
                                                          roles_pages + 0], all_prof_roles[roles_pages + 1], 'Далее',
                                                                                                    'Закончить ввод',
                                                                                                    'Пропустить'))
                except Exception:
                    try:
                        if all_prof_roles[roles_pages + 0]:
                            await callback.message.answer('Выберите профессиональнуые роли',
                                                          reply_markup=inline_keyboard.create_inline_kb(1,
                                                                                                        all_prof_roles[
                                                                                                            roles_pages + 0],
                                                                                                        'Далее',
                                                                                                        'Закончить ввод',
                                                                                                        'Пропустить'))
                    except Exception:
                        try:
                            if all_prof_roles == []:
                                await callback.message.answer('Профессиональные роли не были найдены',
                                                              reply_markup=inline_keyboard.create_inline_kb(1,
                                                                                                            'Пропустить'))
                        except Exception:
                            pass
        await state.set_state(Filters.prof_roles)
    if callback.data == 'Нет':
        await db.add_params(callback.from_user.id, {'test': 'True'})
        filtered_vacancies = await DataProcessor(result, callback.from_user.id).filtered_by_salary()
        filtered_vacancies = await DataProcessor(filtered_vacancies, callback.from_user.id).filtered_by_area()
        filtered_vacancies = await DataProcessor(filtered_vacancies, callback.from_user.id).filtered_by_schedule()
        filtered_vacancies = await DataProcessor(filtered_vacancies, callback.from_user.id).filtered_by_experience()
        filtered_vacancies = await DataProcessor(filtered_vacancies, callback.from_user.id).filetered_by_test()
        all_prof_roles = await DataProcessor(filtered_vacancies, callback.from_user.id).all_prof_roles()
        try:
            await callback.message.answer('Выберите профессиональнуые роли',
                                      reply_markup=inline_keyboard.create_inline_kb(1, all_prof_roles[roles_pages + 0], all_prof_roles[roles_pages + 1], all_prof_roles[roles_pages + 2], all_prof_roles[roles_pages + 3], 'Далее', 'Закончить ввод', 'Пропустить'))
        except IndexError:
            try:
                if all_prof_roles[roles_pages + 0] and all_prof_roles[roles_pages + 1] and all_prof_roles[
                    roles_pages + 2]:
                    await callback.message.answer('Выберите профессиональнуые роли',
                                                  reply_markup=inline_keyboard.create_inline_kb(1, all_prof_roles[
                                                      roles_pages + 0], all_prof_roles[roles_pages + 1], all_prof_roles[
                                                                                                    roles_pages + 2],
                                                                                                'Далее',
                                                                                                'Закончить ввод',
                                                                                                'Пропустить'))
            except Exception:
                try:
                    if all_prof_roles[roles_pages + 0] and all_prof_roles[roles_pages + 1]:
                        await callback.message.answer('Выберите профессиональнуые роли',
                                                      reply_markup=inline_keyboard.create_inline_kb(1, all_prof_roles[
                                                          roles_pages + 0], all_prof_roles[roles_pages + 1], 'Далее',
                                                                                                    'Закончить ввод',
                                                                                                    'Пропустить'))
                except Exception:
                    try:
                        if all_prof_roles[roles_pages + 0]:
                            await callback.message.answer('Выберите профессиональнуые роли',
                                                          reply_markup=inline_keyboard.create_inline_kb(1,
                                                                                                        all_prof_roles[
                                                                                                            roles_pages + 0],
                                                                                                        'Далее',
                                                                                                        'Закончить ввод',
                                                                                                        'Пропустить'))
                    except Exception:
                        try:
                            if all_prof_roles == []:
                                await callback.message.answer('Профессиональные роли не были найдены',
                                                              reply_markup=inline_keyboard.create_inline_kb(1,
                                                                                                            'Пропустить'))
                        except Exception:
                            pass
        await state.set_state(Filters.prof_roles)

@router.callback_query(F.data, Filters.prof_roles)
async def role_input(callback: CallbackQuery, state: FSMContext):
    global roles_pages, all_prof_roles, filtered_vacancies, choosed_roles, button_to_update
    if callback.data not in ['Далее', 'Закончить ввод', 'Пропустить', 'Начало'] and '✅' not in callback.data:
        if ',' in callback.data:
            choosed_roles.append(callback.data.replace(',', ' '))
        else:
            choosed_roles.append(callback.data)
        button_to_update.append(callback.data)
        choosed_roles = list(set(choosed_roles))
    if callback.data not in ['Далее', 'Закончить ввод', 'Пропустить', 'Начало']:

        try:
            await callback.message.edit_reply_markup(callback.inline_message_id,
                                                     reply_markup=inline_keyboard.create_inline_kb(1, all_prof_roles[roles_pages + 0] + '✅' if all_prof_roles[roles_pages + 0] in button_to_update else  all_prof_roles[roles_pages + 0],
                                                                                                   all_prof_roles[roles_pages + 1] + '✅' if all_prof_roles[roles_pages + 1] in button_to_update else all_prof_roles[roles_pages + 1],
                                                                                                   all_prof_roles[roles_pages + 2] + '✅' if all_prof_roles[roles_pages + 2] in button_to_update else all_prof_roles[roles_pages + 2],
                                                                                                   all_prof_roles[roles_pages + 3] + '✅' if all_prof_roles[roles_pages + 3] in button_to_update else all_prof_roles[roles_pages + 3],
                                                                                                   'Далее',
                                                                                                   'Закончить ввод',
                                                                                                   'Пропустить'))
        except IndexError:
            try:
                if all_prof_roles[roles_pages + 0] and all_prof_roles[roles_pages + 1] and all_prof_roles[
                    roles_pages + 2]:
                    await callback.message.edit_reply_markup(callback.inline_message_id,
                                                             reply_markup=inline_keyboard.create_inline_kb(1,
                                                                                                           all_prof_roles[roles_pages + 0] + '✅' if all_prof_roles[roles_pages + 0] in button_to_update else all_prof_roles[roles_pages + 0],
                                                                                                           all_prof_roles[roles_pages + 1] + '✅' if all_prof_roles[roles_pages + 1] in button_to_update else all_prof_roles[roles_pages + 1],
                                                                                                           all_prof_roles[roles_pages + 2] + '✅' if all_prof_roles[roles_pages + 2] in button_to_update else all_prof_roles[roles_pages + 2],
                                                                                                           'Далее',
                                                                                                           'Закончить ввод',
                                                                                                           'Пропустить'))
            except Exception:
                try:
                    if all_prof_roles[roles_pages + 0] and all_prof_roles[roles_pages + 1]:
                        await callback.message.edit_reply_markup(callback.inline_message_id,
                                                                 reply_markup=inline_keyboard.create_inline_kb(1,
                                                                                                               all_prof_roles[roles_pages + 0] + '✅' if all_prof_roles[roles_pages + 0] in button_to_update else all_prof_roles[roles_pages + 0],
                                                                                                               all_prof_roles[roles_pages + 1] + '✅' if all_prof_roles[roles_pages + 1] in button_to_update else all_prof_roles[roles_pages + 1],
                                                                                                               'Далее',
                                                                                                               'Закончить ввод',
                                                                                                               'Пропустить'))
                except Exception:
                    try:
                        if all_prof_roles[roles_pages + 0]:
                            await callback.message.edit_reply_markup(callback.inline_message_id,
                                                                     reply_markup=inline_keyboard.create_inline_kb(1,
                                                                                                                   all_prof_roles[roles_pages + 0] + '✅' if all_prof_roles[roles_pages + 0] in button_to_update else all_prof_roles[roles_pages + 0],
                                                                                                                   'Далее',
                                                                                                                   'Закончить ввод',
                                                                                                                   'Пропустить'))
                    except Exception:
                        try:
                            if all_prof_roles == []:
                                await callback.message.answer('Профессиональные роли не были найдены',
                                                              reply_markup=inline_keyboard.create_inline_kb(1,
                                                                                                            'Пропустить'))
                        except Exception:
                            pass
    if callback.data == 'Закончить ввод':
        await db.add_params(callback.from_user.id, {'prof_roles': ','.join(choosed_roles)})
        await callback.message.answer('Вы заполнили все фильтры, желаете посмотреть вакансии?', reply_markup=inline_keyboard.create_inline_kb(1, 'Показать'))
        await state.set_state(Filters.show_filtered)
    if callback.data == 'Далее':
        roles_pages += 4
        try:
            await callback.message.edit_text('Выберите профессиональнуые роли',
                                      reply_markup=inline_keyboard.create_inline_kb(1, all_prof_roles[roles_pages + 0], all_prof_roles[roles_pages + 1], all_prof_roles[roles_pages + 2], all_prof_roles[roles_pages + 3], 'Далее', 'Закончить ввод', 'Пропустить'))
        except IndexError:
            try:
                if all_prof_roles[roles_pages + 0] and all_prof_roles[roles_pages + 1] and all_prof_roles[
                    roles_pages + 2]:
                    await callback.message.edit_text('Выберите профессиональнуые роли',
                                                  reply_markup=inline_keyboard.create_inline_kb(1, all_prof_roles[
                                                      roles_pages + 0], all_prof_roles[roles_pages + 1], all_prof_roles[
                                                                                                    roles_pages + 2],
                                                                                                'Далее',
                                                                                                'Закончить ввод',
                                                                                                'Пропустить'))
            except Exception:
                try:
                    if all_prof_roles[roles_pages + 0] and all_prof_roles[roles_pages + 1]:
                        await callback.message.edit_text('Выберите профессиональнуые роли',
                                                      reply_markup=inline_keyboard.create_inline_kb(1, all_prof_roles[
                                                          roles_pages + 0], all_prof_roles[roles_pages + 1], 'Далее',
                                                                                                    'Закончить ввод',
                                                                                                    'Пропустить'))
                except Exception:
                    try:
                        if all_prof_roles[roles_pages + 0]:
                            await callback.message.edit_text('Выберите профессиональнуые роли',
                                                          reply_markup=inline_keyboard.create_inline_kb(1,
                                                                                                        all_prof_roles[
                                                                                                            roles_pages + 0],
                                                                                                        'Далее',
                                                                                                        'Закончить ввод',
                                                                                                        'Пропустить'))
                    except Exception:
                        pass
        await state.set_state(Filters.prof_roles)
    if callback.data == 'Начало':
        roles_pages = 0
        try:
            await callback.message.edit_text('Выберите профессиональнуые роли',
                                      reply_markup=inline_keyboard.create_inline_kb(1, all_prof_roles[roles_pages + 0], all_prof_roles[roles_pages + 1], all_prof_roles[roles_pages + 2], all_prof_roles[roles_pages + 3], 'Далее', 'Закончить ввод', 'Пропустить'))
        except IndexError:
            try:
                if all_prof_roles[roles_pages + 0] and all_prof_roles[roles_pages + 1] and all_prof_roles[
                    roles_pages + 2]:
                    await callback.message.edit_text('Выберите профессиональнуые роли',
                                                  reply_markup=inline_keyboard.create_inline_kb(1, all_prof_roles[
                                                      roles_pages + 0], all_prof_roles[roles_pages + 1], all_prof_roles[
                                                                                                    roles_pages + 2],
                                                                                                'Далее',
                                                                                                'Закончить ввод',
                                                                                                'Пропустить'))
            except Exception:
                try:
                    if all_prof_roles[roles_pages + 0] and all_prof_roles[roles_pages + 1]:
                        await callback.message.edit_text('Выберите профессиональнуые роли',
                                                      reply_markup=inline_keyboard.create_inline_kb(1, all_prof_roles[
                                                          roles_pages + 0], all_prof_roles[roles_pages + 1], 'Далее',
                                                                                                    'Закончить ввод',
                                                                                                    'Пропустить'))
                except Exception:
                    try:
                        if all_prof_roles[roles_pages + 0]:
                            await callback.message.edit_text('Выберите профессиональнуые роли',
                                                          reply_markup=inline_keyboard.create_inline_kb(1,
                                                                                                        all_prof_roles[
                                                                                                            roles_pages + 0],
                                                                                                        'Далее',
                                                                                                        'Закончить ввод',
                                                                                                        'Пропустить'))
                    except Exception:
                        pass
        await state.set_state(Filters.prof_roles)
    if callback.data == 'Пропустить':
        await db.add_params(callback.from_user.id, {'prof_roles': 'Пропустить'})
        await callback.message.answer('Вы заполнили все фильтры, желаете посмотреть вакансии?', reply_markup=inline_keyboard.create_inline_kb(1, 'Показать'))
        await state.set_state(Filters.show_filtered)

@router.callback_query(F.data, Filters.show_filtered)
async def show_filtered(callback: CallbackQuery, state: FSMContext):
    global filtered_pages, filtered_vacancies, choosed_roles, button_to_update
    filtered_vacancies = await DataProcessor(filtered_vacancies, callback.from_user.id).filetered_by_role()
    try:
        await callback.message.answer(text = f'<b>{filtered_vacancies[filtered_pages+0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages+0][1])}\n{filtered_vacancies[filtered_pages+0][7]}'
                                            f'\n\n<b>{filtered_vacancies[filtered_pages+1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages+1][1])}\n{filtered_vacancies[filtered_pages+1][7]}'
                                            f'\n\n<b>{filtered_vacancies[filtered_pages+2][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages+2][1])}\n{filtered_vacancies[filtered_pages+2][7]}\n\n'
                                            f'<b>{filtered_vacancies[filtered_pages+3][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages+3][1])}\n{filtered_vacancies[filtered_pages+3][7]}\n\n'
                                            f'<b>{filtered_vacancies[filtered_pages+4][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages+4][1])}\n{filtered_vacancies[filtered_pages+4][7]}',
                                     reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
    except IndexError:
        try:
            if len(filtered_vacancies) == 0:
                await callback.message.edit_text('Найдено 0 вакансий', reply_markup=inline_keyboard.create_inline_kb(1, 'Закрыть'))
                filtered_vacancies = []
            if filtered_vacancies[filtered_pages + 0] and (not filtered_vacancies[filtered_pages + 1]) and (not filtered_vacancies[filtered_pages + 2]) and (not filtered_vacancies[filtered_pages + 3]):
                await callback.message.edit_text(
                    text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}',
                        reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
            if filtered_vacancies[filtered_pages + 0] and filtered_vacancies[filtered_pages + 1]:
                await callback.message.edit_text(
                    text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                         f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}',
                    reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
            if filtered_vacancies[filtered_pages + 0] and filtered_vacancies[filtered_pages + 1] and filtered_vacancies[filtered_pages + 2]:
                await callback.message.edit_text(
                    text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                         f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}'
                         f'\n\n<b>{filtered_vacancies[filtered_pages + 2][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 2][1])}\n{filtered_vacancies[filtered_pages + 2][7]}\n\n',
                    reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
            if filtered_vacancies[filtered_pages + 0] and filtered_vacancies[filtered_pages + 1] and filtered_vacancies[filtered_pages + 2] and filtered_vacancies[filtered_pages + 3]:
                await callback.message.edit_text(
                    text=f'<b>{filtered_vacancies[filtered_pages + 0][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 0][1])}\n{filtered_vacancies[filtered_pages + 0][7]}'
                         f'\n\n<b>{filtered_vacancies[filtered_pages + 1][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 1][1])}\n{filtered_vacancies[filtered_pages + 1][7]}'
                         f'\n\n<b>{filtered_vacancies[filtered_pages + 2][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 2][1])}\n{filtered_vacancies[filtered_pages + 2][7]}\n\n'
                         f'<b>{filtered_vacancies[filtered_pages + 3][0]}</b>\n{if_salary_none(filtered_vacancies[filtered_pages + 3][1])}\n{filtered_vacancies[filtered_pages + 3][7]}\n\n',
                    reply_markup=inline_keyboard.create_inline_kb(2, 'Дальше', 'Начало', 'Закрыть'))
        except IndexError:
            pass
    await state.set_state(Filters.show_more_filtered)

@router.callback_query(F.data.in_(['Дальше', 'Начало', 'Закрыть']), Filters.show_more_filtered)
async def look_filtered(callback: CallbackQuery, state: FSMContext):
    global filtered_vacancies, filtered_pages, result, choosed_roles, roles_pages
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
        await state.set_state(Filters.show_more_filtered)
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
        await state.set_state(Filters.show_more_filtered)
    if callback.data == 'Закрыть':
        result = await db.all_vacancies(callback.from_user.id)
        text1 = '✅Сбор вакансий завершён!\n' \
                'Мы нашли ряд вакансий, которые могут быть интересны именно тебе. Что ты предпочитаешь сделать дальше?' \
                '\n1️⃣Показать Вакансии - Могу отобразить список найденных вакансий.' \
                '\n2️⃣Аналитическая Статистика - Могу предоставить аналитическую статистику по результатам поиска.' \
                '\n3️⃣Ввести Рекомендации - Можешь ввести дополнительные рекомендации, чтобы уточнить критерии поиска.'
        await callback.message.edit_text(text=text1, reply_markup=inline_keyboard.create_inline_kb(2, 'Вывести аналитику',
                                                                                          'Отобразить вакансии',
                                                                                          'Рекомендации поиска',
                                                                                          'Сохраненный поиск',
                                                                                          'Вернуться в главное меню'))
        await state.clear()
        filtered_vacancies = []
        filtered_pages = 0
        choosed_roles = []
        button_to_update = []
        city_pages = 0
        roles_pages = 0


@router.callback_query(F.data == 'Отобразить вакансии')
async def displat_vacancies(callback: CallbackQuery):
    global result
    vacancies = await db.all_vacancie_pagination(callback.from_user.id, page)
    text = []
    for vacancie in vacancies:
        print(vacancie)
        text.append(f'{vacancie[0]}\n{if_salary_none(vacancie[1])}\n{vacancie[7]}')
    text_msg = '\n\n'.join(text)
    await callback.message.edit_text(text = text_msg,
                                     reply_markup=inline_keyboard.create_inline_kb(2, 'Следующая страница', 'В начало', 'В меню'))

page = 0
@router.callback_query(F.data == 'Следующая страница')
async def displat_vacancies(callback: CallbackQuery):
    global page
    page += 5
    vacancies = await db.all_vacancie_pagination(callback.from_user.id, page)
    text = []
    for vacancie in vacancies:
        text.append(f'{vacancie[0]}\n{if_salary_none(vacancie[1])}\n{vacancie[7]}')
    text_msg = '\n\n'.join(text)
    await callback.message.edit_text(
        text=text_msg,
        reply_markup=inline_keyboard.create_inline_kb(2, 'Следующая страница', 'В начало', 'В меню'))


@router.callback_query(F.data == 'В начало')
async def first_page_vacancies(callback: CallbackQuery):
    page = 0
    vacancies = await db.all_vacancie_pagination(callback.from_user.id, page)
    text = []
    for vacancie in vacancies:
        text.append(f'{vacancie[0]}\n{if_salary_none(vacancie[1])}\n{vacancie[7]}')
    text_msg = '\n\n'.join(text)
    await callback.message.edit_text(
        text= text_msg,
        reply_markup=inline_keyboard.create_inline_kb(2, 'Следующая страница', 'В начало', 'В меню'))


@router.callback_query(F.data == 'Вернуться в главное меню')
async def menu_button(callback: CallbackQuery):
    global result
    await db.delete_vacancies_by_id(callback.from_user.id)
    await callback.message.delete()
    await callback.message.bot.send_photo(chat_id=callback.from_user.id, photo=FSInputFile('static/hh.jpg'),
                                 caption='🌐Главное Меню\nВыбери интересующий тебя раздел, используя кнопки ниже:\n'
                                         '🔍 Поиск Вакансий - Начни поиск работы, указав желаемую должность или ключевые слова'
                                         '\n⚙️ Настройки - Настрой параметры поиска вакансий и частоту уведомлений.'
                                         '\n📄 Работа с Резюме - Управляй своими резюме, обновляй их, включай мониторинг просмотров.\n'
                                         '🚫 Забыть Меня - Удали всю свою информацию из базы данных бота.'
                                         '\n✉️ Обратная Связь - Отправь свои вопросы, предложения или отзывы создателю бота.'
                                         '\n🤖 Я здесь, чтобы помочь тебе найти идеальную работу.',
                                 reply_markup=inline_keyboard.create_inline_kb(2, 'Поиск вакансий', 'Работа с резюме', 'Настройки пользователя', 'Забыть меня', 'Обратная связь'))
    result = []

@router.message(Command('clear'))
async def clear_all(message: Message, state: FSMContext):
    await state.clear()
    global filtered_vacancies, result, roles_pages, filtered_pages, city_pages
    city_pages = 0
    filtered_pages = 0
    roles_pages = 0
    filtered_vacancies = []
    result = []
    await message.bot.send_photo(chat_id=message.from_user.id, photo=FSInputFile('static/hh.jpg'),
                                 caption='🌐Главное Меню\nВыбери интересующий тебя раздел, используя кнопки ниже:\n'
                                         '🔍 Поиск Вакансий - Начни поиск работы, указав желаемую должность или ключевые слова'
                                         '\n⚙️ Настройки - Настрой параметры поиска вакансий и частоту уведомлений.'
                                         '\n📄 Работа с Резюме - Управляй своими резюме, обновляй их, включай мониторинг просмотров.\n'
                                         '🚫 Забыть Меня - Удали всю свою информацию из базы данных бота.'
                                         '\n✉️ Обратная Связь - Отправь свои вопросы, предложения или отзывы создателю бота.'
                                         '\n🤖 Я здесь, чтобы помочь тебе найти идеальную работу.',
                                 reply_markup=inline_keyboard.create_inline_kb(2, 'Поиск вакансий', 'Работа с резюме', 'Настройки пользователя', 'Забыть меня', 'Обратная связь'))