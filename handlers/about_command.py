from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from keyboards import inline_keyboard, keyboards
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

@router.message(Command('about'))
async def about_coommand(message: Message):
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