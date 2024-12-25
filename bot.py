import asyncio
import logging
from aiogram import Bot, Dispatcher
from handlers import resume, vacancies_find_button, saved_search_button, analytic_handler, user_options, about_command
from database.database import async_main
from middlewares.middlewares import Changelogs
from aiogram.types import BotCommand
from models.models import Users, UserVacancies, FilterLogs
from sqlalchemy import select, update
from loguru import logger as log
from handlers.notifications_vacancies import main
from handlers.autoupdate_resumes import update_resume
from handlers.views_notifications import notifications_worker
from database.database import async_main
import aiocron


logging.basicConfig(
  level=logging.DEBUG,
  format='%(filename)s:%(lineno)d #%(levelname)-8s '
         '[%(asctime)s] - %(name)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info('Starting bot')
bot = Bot(token='',
          parse_mode='HTML')
dp = Dispatcher()
vacancies_find_button.router.callback_query.middleware(Changelogs())
dp.include_routers(vacancies_find_button.router, analytic_handler.router, saved_search_button.router, user_options.router, resume.router)


async def start_bot():
    # Запускаем polling бота
    await dp.start_polling(bot)

async def run():
    await async_main()
    await asyncio.gather(main(bot), start_bot(), update_resume(bot), notifications_worker(bot))

if __name__ == '__main__':
    asyncio.run(run())
