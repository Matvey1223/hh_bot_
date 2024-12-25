from api.work_with_resumes import WorkWithResumes
import asyncio
from database.database import async_session
from models.models import Users, UserResumes
from sqlalchemy import select
from loguru import logger


async def send_notification(user_id, bot):
    while True:
        async with async_session() as session:
            users_enabled_resumes = await session.execute(select(UserResumes.title, UserResumes.resume_id).where(UserResumes.user_id == user_id).where(UserResumes.monitoring_views == True))
            enabled = users_enabled_resumes.fetchall()
            user_interval_monitoring = await session.execute(select(Users.monitoring_resume_interval, Users.token).where(Users.id == user_id))
            user_interval_monitoring = user_interval_monitoring.fetchone()
            if enabled != []:
                for i in enabled:
                    views = await WorkWithResumes(user_interval_monitoring[1]).recent_look_views(i[1], user_interval_monitoring[0])
                    await bot.send_message(user_id, f'У вас {len(views)} новых просмотров на резюме {i[0]} за последние {user_interval_monitoring[0]} часов')
            else:
                logger.info(f"Notifications are disabled for user {user_id}")
        await asyncio.sleep(user_interval_monitoring[0])

async def check_users(last_checked_user_id):
    async with async_session() as session:
        users = await session.execute(select(Users.id).where(Users.id != last_checked_user_id))
        users = users.fetchall()
        return users


async def notifications_worker(bot):
    last_checked_user_id = 0  # Переменная для хранения ID последнего проверенного пользователя
    while True:
        users = await check_users(last_checked_user_id)
        for user in users:
            user_id = user[0]
            asyncio.create_task(send_notification(user_id, bot))

            if user_id != last_checked_user_id:
                last_checked_user_id = user_id

        await asyncio.sleep(20)# await asyncio.sleep(1)  # Проверяем новых пользователей каждую секунду
