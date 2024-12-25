import datetime
import os
from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile
from analytic.analytic_module import Analytic
import asyncio


router = Router()

async def execute_analytics(user_id):
    tasks = [
        Analytic(user_id).show_vacs_by_experience(),
        Analytic(user_id).show_graphic_by_city(),
        Analytic(user_id).with_or_no_salary_diagramm(),
        Analytic(user_id).show_top_10_companies(),
        Analytic(user_id).show_shedule(),
        Analytic(user_id).show_employment(),
        Analytic(user_id).top_10_prof_roles(),
        Analytic(user_id).salaries_analytic()
    ]
    results = await asyncio.gather(*tasks)
    return results

@router.callback_query(F.data == 'Вывести аналитику')
async def show_analytic(callback: CallbackQuery):
    await execute_analytics(callback.from_user.id)
    await callback.message.answer('🔍Анализирую найденные вакансии... Подготавливаю всю необходимую статистику, чтобы ты мог сделать осознанный выбор!')
    for i in range(8):
        await callback.bot.send_photo(photo=FSInputFile(f'analytic/result/{i + 1}_{callback.from_user.id}.png'), chat_id=callback.from_user.id)
        folder_path = 'analytic/result'
        file_path = os.path.join(folder_path, f'{i + 1}_{callback.from_user.id}.png')
        os.remove(file_path)
