from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, FSInputFile
from keyboards import inline_keyboard
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from api.work_with_resumes import WorkWithResumes
from authlib.oauth2 import OAuth2Client
import httpx
from database.database import async_session
from models.models import Users, UserResumes
from sqlalchemy import select, update, insert



router = Router()

HH_CLIENT_ID = "K30VSKO0FJ0NGKN2N2RQJA0Q7LUOJJM5DNEM5JHFU47ADM16IPGEBSRO59DAVHPQ"
HH_CLIENT_SECRET = "TIJ2QVINV13LVF9TMPJ5T4Q1DVRJU0I44SHS4HTAMO6F3JGSH5GRD3VG9I1VO9DV"
HH_AUTHORIZATION_URL = "https://hh.ru/oauth/authorize"
HH_TOKEN_URL = "https://hh.ru/oauth/token"
HH_REDIRECT_URI = "http://localhost:8000/redirect"
session = httpx.AsyncClient()
oauth_client = OAuth2Client(client_id=HH_CLIENT_ID, client_secret=HH_CLIENT_SECRET, session=session)
choosed_resume = ''


class ResumesChoose(StatesGroup):
    resume = State()


@router.callback_query(F.data == 'Работа с резюме', StateFilter(None))
async def resume_check_token(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        if_token = await session.execute(select(Users.token).where(Users.id == callback.from_user.id))
        if_token = if_token.fetchone()
    if if_token[0] != None:
        all_resumes = await WorkWithResumes(if_token[0]).get_all_resumes()
        titles = list(all_resumes.keys())
        await callback.message.answer('✅ Получил твои резюме! Пожалуйста, выбери одно из них для дальнейшей работы или обновления.', reply_markup=inline_keyboard.create_inline_kb(1,*titles))
        await state.set_state(ResumesChoose.resume)
    else:
        authorization_url = oauth_client.create_authorization_url(HH_AUTHORIZATION_URL, redirect_uri=HH_REDIRECT_URI, state=callback.from_user.id)
        await callback.message.answer(f'Чтобы использовать этот метод, Вам необходимо разрешить нашему боту доступ к Вашим '
                                      f'данным на сайте hh. Продолжая Вы соглашаетесь на передачу своих персональныз данных. <a href="{authorization_url[0]}">Перейдите по сслыке, чтобы передать токен боту</a>', parse_mode='HTML')
        while True:
            async with async_session() as session:
                if_token = await session.execute(select(Users.token).where(Users.id == callback.from_user.id))
                if_token = if_token.fetchone()
            if if_token[0] != None:
                break
        await callback.message.answer('Вы успешно авторизовались.')
        all_resumes = await WorkWithResumes(if_token[0]).get_all_resumes()
        titles = list(all_resumes.keys())
        ids = list(all_resumes.values())
        for i in range(len(titles)):
            await session.execute(insert(UserResumes).values(user_id = callback.from_user.id, title = titles[i], resume_id = ids[i]))
            await session.commit()
        await callback.message.answer('✅ Получил твои резюме! Пожалуйста, выбери одно из них для дальнейшей работы или обновления.', reply_markup=inline_keyboard.create_inline_kb(1, *titles))
        await state.set_state(ResumesChoose.resume)


@router.callback_query(F.data, ResumesChoose.resume)
async def work_with_resume(callback: CallbackQuery, state: FSMContext):
    global choosed_resume
    buttons = ['Вкл/выкл автообновление резюме', 'Вкл/выкл мониторинг просмотров резюме', 'Обновить резюме' , 'Увидеть прсмотры резюме', 'Вернуть обратно']
    datas = ['on_autoupdate_resume', 'on_resume_monitor', 'update_resume', 'look_views', 'back']
    await callback.message.edit_text(text=f'{callback.data}',
                                     reply_markup=inline_keyboard.work_with_resume(1, buttons, datas))
    choosed_resume = callback.data
    await state.clear()


@router.callback_query(F.data == 'update_resume')
async def update_resume(callback: CallbackQuery):
    async with async_session() as session:
        if_token = await session.execute(select(Users.token).where(Users.id == callback.from_user.id))
        if_token = if_token.fetchone()
    response = await WorkWithResumes(if_token[0]).update_resume(callback.message.text)
    if response.status_code == 429:
        await callback.message.answer('🚫Ещё рано для обновления, попробуйте позже!')
    else:
        await callback.message.answer('✅Ваше резюме было обновлено!')

views_pagination = 0
all_views = None
@router.callback_query(F.data == 'look_views')
async def look_views(callback: CallbackQuery):
    global views_pagination, all_views
    async with async_session() as session:
        if_token = await session.execute(select(Users.token).where(Users.id == callback.from_user.id))
        if_token = if_token.fetchone()
    all_views = await WorkWithResumes(if_token[0]).look_views(callback.message.text)
    first_page = '\n'.join(all_views[views_pagination])
    await callback.message.edit_text(text = f'Ваше резюме просмотрели:\n\n{first_page}', inline_message_id=callback.inline_message_id,
                                     reply_markup=inline_keyboard.create_inline_kb(1, 'Обратно', 'Еще просмотры ->'), parse_mode='HTML')

@router.callback_query(F.data == 'Еще просмотры ->')
async def more_views(callback: CallbackQuery):
    global views_pagination, all_views
    views_pagination += 1
    page = '\n'.join(all_views[views_pagination])
    await callback.message.edit_text(text = f'Ваше резюме просмотрели:\n\n{page}', inline_message_id=callback.inline_message_id,
                                     reply_markup=inline_keyboard.create_inline_kb(1, 'Обратно', 'Еще просмотры ->'), parse_mode='HTML')


@router.callback_query(F.data == 'Обратно')
async def back_from_views(callback: CallbackQuery):
    global choosed_resume, all_views, views_pagination
    buttons = ['Вкл/выкл автообновление резюме', 'Вкл/выкл мониторинг просмотров резюме', 'Обновить резюме',
               'Увидеть прсмотры резюме', 'Вернуть обратно']
    datas = ['on_autoupdate_resume', 'on_resume_monitor', 'update_resume', 'look_views', 'back']
    await callback.message.edit_text(text=f'{choosed_resume}',
                                     reply_markup=inline_keyboard.work_with_resume(1, buttons, datas))
    all_views = None
    views_pagination = 0

@router.callback_query(F.data == 'on_autoupdate_resume')
async def autoupdate_resume(callback: CallbackQuery):
    async with async_session() as session:
        autoupdate_status = await session.execute(select(UserResumes.autoupdate).where(UserResumes.user_id == callback.from_user.id).where(UserResumes.title == callback.message.text))
        autoupdate_status = autoupdate_status.fetchone()
        if autoupdate_status[0] == False:
            await session.execute(update(UserResumes).values(autoupdate = True).where(UserResumes.user_id == callback.from_user.id).where(UserResumes.title == callback.message.text))
            await session.commit()
            await callback.message.answer('✅ Автообновление резюме было включено!')
        if autoupdate_status[0] == True:
            await session.execute(update(UserResumes).values(autoupdate = False).where(UserResumes.user_id == callback.from_user.id).where(UserResumes.title == callback.message.text))
            await session.commit()
            await callback.message.answer('🚫 Автообновление резюме было выключено!')

@router.callback_query(F.data == 'on_resume_monitor')
async def monitor_views_notifications(callback: CallbackQuery):
    async with async_session() as session:
        monitor_status = await session.execute(select(UserResumes.monitoring_views).where(UserResumes.user_id == callback.from_user.id).where(UserResumes.title == callback.message.text))
        monitor_status = monitor_status.fetchone()
    if monitor_status[0] == False:
        async with async_session() as session:
            await session.execute(update(UserResumes).values(monitoring_views = True).where(UserResumes.user_id == callback.from_user.id).where(UserResumes.title == callback.message.text))
            await session.commit()
        await callback.message.answer('✅Мониторинг новых просмотров резюме был включен!')
    if monitor_status[0] == True:
        async with async_session() as session:
            await session.execute(update(UserResumes).values(monitoring_views=False).where(UserResumes.user_id == callback.from_user.id).where(UserResumes.title == callback.message.text))
            await session.commit()
        await callback.message.answer('🚫 Мониторинг новых просмотров резюме был выключен!')

@router.callback_query(F.data == 'back')
async def back_button(callback: CallbackQuery):
    global choosed_resume, views_pagination, all_views
    await callback.message.bot.send_photo(chat_id=callback.from_user.id, photo=FSInputFile('static/hh.jpg'),
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
    choosed_resume =''
    views_pagination = 0
    all_views = None









