import requests
from datetime import datetime, timezone, timedelta


class WorkWithResumes():
    def __init__(self, token):
        self.token = token

    async def get_all_resumes(self):
        resume_url = 'https://api.hh.ru/resumes/mine'

        # Заголовки запроса, включая авторизационный токен
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        # Отправка GET запроса к API hh.ru
        response = requests.get(resume_url, headers=headers)
        resume_data = response.json()
        all_resume = [i['title'] for i in resume_data['items']]
        all_ids = [i['id'] for i in resume_data['items']]
        result = {}
        for i in range(len(all_resume)):
            result[all_resume[i]] = all_ids[i]
        return result

    async def update_resume(self, name):
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        # Отправка GET запроса к API hh.ru
        response = requests.get('https://api.hh.ru/resumes/mine', headers=headers)
        resume_data = response.json()
        resume_id = ''
        for i in resume_data['items']:
            if i['title'] == name:
                resume_id = i['id']
        response = requests.post(url = f'https://api.hh.ru/resumes/{resume_id}/publish', headers=headers)
        return response

    async def look_views(self, name):
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        response = requests.get('https://api.hh.ru/resumes/mine', headers=headers)
        resume_data = response.json()
        resume_id = ''
        for i in resume_data['items']:
            if i['title'] == name:
                resume_id = i['id']
        resume_view_history_url = f'https://api.hh.ru/resumes/{resume_id}/views'

        # Отправка GET запроса к API hh.ru для получения истории просмотров резюме
        response = requests.get(resume_view_history_url, headers=headers)
        view_history = response.json()
        items = view_history['items']
        grouped_items = [items[i:i + 5] for i in range(0, len(items), 5)]
        for i in range(len(grouped_items)):
            for j in range(len(grouped_items[i])):
                employer_name = grouped_items[i][j]['employer']['name']
                employer_url = grouped_items[i][j]['employer']['alternate_url']
                created_at = str(grouped_items[i][j]['created_at'])
                grouped_items[i][j] = f'<a href="{employer_url}">{employer_name}</a> {created_at}'
        return grouped_items

    async def recent_look_views(self, resume_id, interval: int):
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        resume_view_history_url = f'https://api.hh.ru/resumes/{resume_id}/views'

        # Отправка GET запроса к API hh.ru для получения истории просмотров резюме
        response = requests.get(resume_view_history_url, headers=headers)
        view_history = response.json()
        current_time = datetime.now().replace(tzinfo=timezone.utc)  # Приводим к offset-aware формату

        # Определяем временной интервал в 2 часа
        time_threshold = current_time - timedelta(hours=interval)

        # Фильтруем просмотры резюме, оставляем только те, которые были получены в течение последних 2 часов
        recent_resume_views = [view for view in view_history['items'] if
                               datetime.fromisoformat(view["created_at"]) >= time_threshold]
        return recent_resume_views

