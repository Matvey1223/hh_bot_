import asyncio
import aiohttp
import json
from datetime import datetime, timedelta




async def get_city_id(city):
    with open('areas.json', encoding='utf-8') as file:
        data = json.load(file)
    if city == 'Москва':
        return 1
    if city == 'Санкт-Петербург':
        return 1
    if city != 'Москва' and city != 'Санкт-Петербург':
        for i in data[0]['areas']:
            for j in i['areas']:
                if j['name'] == city:
                    return j['id']

async def get_experience_id(experience):
    with open('dictionaries.json', encoding='utf-8') as file:
        data = json.load(file)
    for i in data['experience']:
        if i['name'] == experience:
            return i['id']

async def get_schedule_id(schedule):
    with open('dictionaries.json', encoding='utf-8') as file:
        data = json.load(file)
    for i in data['schedule']:
        if i['name'] == schedule:
            return i['id']

async def fetch_jobs(filter, interval):
    text = filter[0]
    salary = filter[1]
    city_id = await get_city_id(filter[2])
    schedule = await get_schedule_id(filter[3])
    experience = await get_experience_id(filter[4])
    if '-' in salary:
        params = {'text': text, 'salary': int(salary.split('-')[0]), 'area': city_id, 'experience': experience, 'schedule': schedule, 'date_from': str((datetime.now() - timedelta(hours=interval)).strftime('%Y-%m-%dT%H:%M:%S')), 'date_to': str(datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))}
    else:
        params = {'text': text, 'salary': int(salary), 'area': city_id, 'experience': experience, 'schedule': schedule, 'date_from': str((datetime.now() - timedelta(hours=interval)).strftime('%Y-%m-%dT%H:%M:%S')), 'date_to': str(datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))}
    url = "https://api.hh.ru/vacancies"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params = params) as response:
            return await response.json()

async def get_jobs(filters, interval):
    tasks = [fetch_jobs(filter, interval) for filter in filters]
    results = await asyncio.gather(*tasks)
    return results

async def main(filters, interval):
    results = await get_jobs(filters, interval)
    return results # Обработка полученных данных