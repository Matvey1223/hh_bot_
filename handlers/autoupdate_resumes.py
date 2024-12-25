import asyncio
from database.database import async_session
from models.models import UserResumes, Users
from sqlalchemy import select
from loguru import logger
from api.work_with_resumes import WorkWithResumes


async def update_resume(bot):
    while True:
        async with async_session() as session:
            all_resumes = await session.execute(select(UserResumes.user_id, UserResumes.title).where(UserResumes.autoupdate == True))
            all_resumes = all_resumes.fetchall()
        logger.info(all_resumes)
        for i in all_resumes:
            token = await session.execute(select(Users.token).where(Users.id == i[0]))
            token = token.fetchone()
            await WorkWithResumes(token[0]).update_resume(i[1])
            try:
                await bot.send_message(i[0], "Ваше резюме было обновлено!")
            except Exception as ex:
                pass
        await asyncio.sleep(10)












