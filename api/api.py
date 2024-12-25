import aiohttp
import asyncio
from itertools import product


experience_levels = ['noExperience', 'between1And3', 'between3And6', 'moreThan6']
schedule_types = ['fullDay', 'shift', 'flexible', 'remote', 'flyInFlyOut']


async def fetch_vacancies(session, text, additional_filters=None):
    all_vacancies = []
    url = "https://api.hh.ru/vacancies"
    page = 0
    while True:
        params = {'text': text, 'page': page, 'per_page': 100, 'area': 113}
        if additional_filters:
            params.update(additional_filters)
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                all_vacancies.extend(data['items'])
                if page >= data['pages'] - 1:
                    break
                page += 1
            else:
                break
            await asyncio.sleep(1)  # Соблюдайте задержку между запросами
    return all_vacancies

async def main(text, filters_list):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_vacancies(session, text, additional_filters=filters) for filters in filters_list]
        results = await asyncio.gather(*tasks)
        # Объедините результаты всех задач
        all_vacancies = [item for sublist in results for item in sublist]
        return all_vacancies


# Запуск асинхронного сбора данных
async def run(text):
    filters_list = []
    for shedule, experience in list(product(schedule_types, experience_levels)):
        filters_list.append({'experience': experience, 'shedule': shedule})
    vacancies = await main(text, filters_list)
    print(f"Найдено {len(vacancies)} вакансий.")
    return vacancies




