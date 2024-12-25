from api.notifications_api import main as notifications
from ast import literal_eval
import asyncio
from database.database import async_session
from models.models import Users, FilterLogs
from sqlalchemy import select
from loguru import logger


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

async def send_notification(user_id, bot):
    while True:
        async with async_session() as session:
            enabled = await session.execute(select(Users.id, Users.new_vacancies_notification, Users.freq_new_vacancy_notifications).where(Users.id == user_id))
            enabled = enabled.fetchone()
            if enabled[1]:  # Проверяем, что уведомления включены для пользователя
                logger.info(f"Sending notification to user {user_id}")
                user_filters = await session.execute(select(FilterLogs.text, FilterLogs.salary, FilterLogs.city, FilterLogs.schedule, FilterLogs.experience, FilterLogs.test, FilterLogs.prof_role)
                                                     .where(FilterLogs.user_id == user_id).where(FilterLogs.for_notifications == True).order_by(FilterLogs.created_at))
                user_filters = user_filters.fetchall()
                vacancies = await notifications(user_filters, enabled[2])
                if vacancies[0]:
                    for i in range(len(vacancies)):
                        if vacancies[i]['items'] == []:
                            await bot.send_message(user_id, text=f'Новых вакансий не найдено по фильтру\n Город: {user_filters[i][2]}, Зарплата: {str(user_filters[i][1])}, График: {user_filters[i][3]}, Опыт: {user_filters[i][4]}')
                        else:
                            text = []
                            for j in vacancies[i]['items']:
                                text.append([j['name'], if_salary_none(str(j['salary'])), j['alternate_url']])
                            text = ['\n'.join(i) for i in text]
                            text = '\n\n'.join(text)
                            await bot.send_message(user_id, text =f'Найдены новые вакансии по фильтру\n Город: {user_filters[i][2]}, Зарплата: {str(user_filters[i][1])}, График: {user_filters[i][3]}, Опыт: {user_filters[i][4]}\n\n{text}')
                else: logger.info('No vacancies founded')
            else:
                logger.info(f"Notifications are disabled for user {user_id}")

            await asyncio.sleep(enabled[2])


async def check_users(last_checked_user_id):
    async with async_session() as session:
        users = await session.execute(select(Users.id).where(Users.id != last_checked_user_id))
        users = users.fetchall()
        return users


async def main(bot):
    last_checked_user_id = 0  # Переменная для хранения ID последнего проверенного пользователя
    while True:
        users = await check_users(last_checked_user_id)
        for user in users:
            user_id = user[0]
            asyncio.create_task(send_notification(user_id, bot))

            if user_id != last_checked_user_id:
                last_checked_user_id = user_id

        await asyncio.sleep(20)# Проверяем новых пользователей каждую секунду










