import math
from .database import async_session
from models.models import Users, UserVacancies, FilterLogs
from sqlalchemy import insert, select, update, delete, func
from ast import literal_eval


async def add_user(id, username):  # регаем юзера
    async with async_session() as session:
        query = select(Users).where(Users.id == id)
        result = await session.execute(query)
        existing_user = result.scalar()
        if existing_user is None:
            await session.execute(insert(Users).values(id=id, username=username))
            await session.commit()


async def add_vacancies(id: int, vacancies: list):  # после парсинга всех вакансий вставляем результат в таблицу
    async with async_session() as session:
        for i in vacancies:
            await session.execute(insert(UserVacancies).values(user_id=id, salary=str(i['salary']), name=i['name'],
                                                               city=i['area']['name'], schedule=i['schedule']['name'],
                                                               experience=i['experience']['name'],
                                                               employment=i['employment']['name'], test=i['has_test'],
                                                               prof_role=i['professional_roles'][0]['name'],
                                                               url=i["alternate_url"], company=i['employer']['name']))
            await session.commit()


async def all_vacancie_pagination(id, page):
    async with async_session() as session:
        query = select(UserVacancies.name, UserVacancies.salary, UserVacancies.city, UserVacancies.schedule,
                       UserVacancies.experience, UserVacancies.test, UserVacancies.prof_role,
                       UserVacancies.url).order_by(UserVacancies.id).where(UserVacancies.user_id == id).limit(5).offset(
            page)
        five_vacancies = await session.execute(query)
        result = five_vacancies.fetchall()
        await session.commit()
    return result


async def all_vacancies(id):
    async with async_session() as session:
        query = select(UserVacancies.name, UserVacancies.salary, UserVacancies.city, UserVacancies.schedule,
                       UserVacancies.experience, UserVacancies.test, UserVacancies.prof_role,
                       UserVacancies.url).order_by(UserVacancies.id).where(UserVacancies.user_id == id)
        vacancies = await session.execute(query)
        result = vacancies.fetchall()
    return result


async def cities(id):  # все города
    async with async_session() as session:
        query = select(UserVacancies.city).where(UserVacancies.user_id == id)
        cities = await session.execute(query)
        result = cities.fetchall()
        await session.commit()
    return list(set([i[0] for i in result]))


async def all_prof_roles(id, vacancies: list):  # все проф роли
    async with async_session() as session:
        query = select(UserVacancies.prof_role).where(UserVacancies.user_id == id and UserVacancies.city == city)
        roles = await session.execute(query)
        result = roles.fetchall()
        await session.commit()
    result = list(set([i[0] for i in result]))
    roles = []
    for i in result:
        if len(i) > 40:
            roles.append(i.split(' ')[0] + ' ' + i.split(' ')[1])
        else:
            roles.append(i)
    return roles


async def add_user_text_api(user_id, text):
    async with async_session() as session:
        query = update(Users).where(Users.id == int(user_id)).values(
            text=text)  # Создаем операцию вставки с указанием значения и условия
        await session.execute(query)  # Выполняем операцию вставки
        await session.commit()


async def add_params(user_id, attribute: dict):  # вместо add_salary, add_city и т.д.
    async with async_session() as session:
        query = update(Users).where(Users.id == int(user_id)).values(attribute)
        await session.execute(query)
        await session.commit()


async def select_filters(user_id):
    async with async_session() as session:
        query = select(Users.text, Users.salary, Users.city, Users.shedule, Users.experience, Users.prof_roles,
                       Users.test).where(Users.id == user_id)
        result = await session.execute(query)
        filters = result.fetchall()
        await session.commit()
    return filters


async def delete_vacancies_by_id(id):
    async with async_session() as session:
        query = delete(UserVacancies).where(UserVacancies.user_id == id)
        await session.execute(query)
        await session.commit()


async def add_filter_log(id, text, salary, city, schedule, experience, test, prof_role, time):
    async with async_session() as session:
        query = insert(FilterLogs).values(user_id=id, text=text, salary=salary, city=city, schedule=schedule,
                                          experience=experience, test=test, prof_role=prof_role, created_at=time)
        await session.execute(query)
        await session.commit()


async def manage_filter_logs(id, return_full=False):  # вместо select_logs_filters, len_logs_filters
    async with async_session() as session:
        query = select(FilterLogs.text, FilterLogs.salary, FilterLogs.city, FilterLogs.schedule, FilterLogs.experience,
                       FilterLogs.test, FilterLogs.prof_role).where(FilterLogs.user_id == id).order_by(FilterLogs.id)
        filters = await session.execute(query)
        result = filters.fetchall()
        await session.commit()
    if return_full:
        return result
    else:
        return len(result)


async def change_logs(id, text, salary, city, schedule, experience, test, prof_role, time):
    async with async_session() as session:
        # Находим первый добавленный элемент
        query = select(FilterLogs.id).order_by(FilterLogs.created_at).where(FilterLogs.user_id == id).where(
            FilterLogs.for_notifications == False)
        result = await session.execute(query)
        first_element = result.fetchone()[0]
        await session.commit()
        if first_element:
            await session.execute(
                delete(FilterLogs).where(FilterLogs.id == first_element).where(FilterLogs.for_notifications == False))
            await session.commit()
            await session.execute(
                insert(FilterLogs).values(user_id=id, text=text, salary=salary, city=city, schedule=schedule,
                                          experience=experience, test=test, prof_role=prof_role, created_at=time))
            await session.commit()


async def select_all_vacs_by_experience(user_id):  # Вместо select_all_vacs_by_experience
    async with async_session() as session:
        query = (select(func.count().label('count'),
                        UserVacancies.experience)
                 .where(UserVacancies.user_id == user_id)
                 .group_by(UserVacancies.experience))

        result = await session.execute(query)
        experience_counts = result.fetchall()
        await session.commit()
    counts_by_experience = {exp: 0 for exp in ["Нет опыта", "От 1 года до 3 лет", "От 3 до 6 лет", "Более 6 лет"]}
    for count, experience in experience_counts:
        if experience in counts_by_experience:
            counts_by_experience[experience] = count
    return (
        counts_by_experience["Нет опыта"],
        counts_by_experience["От 1 года до 3 лет"],
        counts_by_experience["От 3 до 6 лет"],
        counts_by_experience["Более 6 лет"]
    )


async def top_5_cities(user_id):
    async with async_session() as session:
        top_5_cities = select(UserVacancies.city).where(UserVacancies.user_id == user_id)
        result = await session.execute(top_5_cities)
        result = result.fetchall()
        result = [i[0] for i in result]
        await session.commit()
        count_dict = {}

        for item in result:
            if item in count_dict:
                count_dict[item] += 1
            else:
                count_dict[item] = 1

        sorted_items = sorted(count_dict.items(), key=lambda x: x[1], reverse=True)[:5]
        sorted_dict = dict(sorted_items)
        return list(sorted_dict.keys())


# вместо select_no_exp_for_top_cities, select_1_3, select_3_6, select_more_6
async def select_exp_for_top_cities(user_id: int, cities: list, experience: str) -> list:
    result_final = []
    async with async_session() as session:
        for city in cities:
            city_len = select(UserVacancies).where(UserVacancies.city == city).where(
                UserVacancies.user_id == user_id).where(UserVacancies.experience == experience)
            result = await session.execute(city_len)
            result_final.append(len(result.fetchall()))
            await session.commit()
    return result_final


async def with_no_salaries(user_id):
    all_vacs = await all_vacancies(user_id)
    with_s = 0
    no_s = 0
    for i in all_vacs:
        if i[1] == 'None':
            no_s += 1
        else:
            with_s += 1
    with_s_percent = with_s / len(all_vacs)
    no_s_persent = no_s / len(all_vacs)
    return (no_s_persent, with_s_percent)


async def top_10_companies(user_id):
    async with async_session() as session:
        top_10_companies = select(UserVacancies.company).where(UserVacancies.user_id == user_id)
        result = await session.execute(top_10_companies)
        result = result.fetchall()
        result = [i[0] for i in result]
        await session.commit()
        count_dict = {}

        for item in result:
            if item in count_dict:
                count_dict[item] += 1
            else:
                count_dict[item] = 1

        sorted_items = sorted(count_dict.items(), key=lambda x: x[1], reverse=True)[:10]
        sorted_dict = dict(sorted_items)
        return list(sorted_dict.keys())


# Вместо функции где top_10_companies
async def exp_top_10_companies(user_id: int, companies: list, experience: str) -> list:
    result_final = []
    async with async_session() as session:
        for companie in companies:
            query = select(UserVacancies).where(UserVacancies.company == companie).where(
                UserVacancies.user_id == user_id).where(UserVacancies.experience == experience)
            result = await session.execute(query)
            result_final.append(len(result.fetchall()))
    return result_final


async def schedule_exps(user_id: int, schedules: list, experience: str) -> list:
    final_result = []
    async with async_session() as session:
        for num in schedules:
            query = select(UserVacancies).where(UserVacancies.schedule == num).where(
            UserVacancies.user_id == user_id).where(UserVacancies.experience == experience)
            result = await session.execute(query)
            final_result.append(len(result.fetchall()))
            await session.commit()
    return final_result


async def employment_analytic(user_id: int, employments: list, experience: str) -> list:
    final_result = []
    async with async_session() as session:
        for num in employments:
            query = select(UserVacancies).where(UserVacancies.employment == num).where(
            UserVacancies.user_id == user_id).where(UserVacancies.experience == experience)
            result = await session.execute(query)
            final_result.append(len(result.fetchall()))
            await session.commit()
    return final_result


async def top_10_prof_roles(user_id):
    async with async_session() as session:
        top_10_prof_roles = select(UserVacancies.prof_role).where(UserVacancies.user_id == user_id)
        result = await session.execute(top_10_prof_roles)
        result = result.fetchall()
        result = [i[0] for i in result]
        await session.commit()
        count_dict = {}

        for item in result:
            if item in count_dict:
                count_dict[item] += 1
            else:
                count_dict[item] = 1

        sorted_items = sorted(count_dict.items(), key=lambda x: x[1], reverse=True)[:10]
        sorted_dict = dict(sorted_items)
        return list(sorted_dict.keys())


async def show_prof_roles_analytic(user_id: int, top_10: list, experience: str) -> list:
    final_result = []
    async with async_session() as session:
        for num in top_10:
            query = select(UserVacancies).where(UserVacancies.prof_role == num).where(
                UserVacancies.user_id == user_id).where(UserVacancies.experience == experience)
            result = await session.execute(query)
            final_result.append(len(result.fetchall()))
            await session.commit()
    return final_result


async def salaries_analytic(user_id, experience):
    async with async_session() as session:
        query = select(UserVacancies.salary).where(UserVacancies.salary != 'None').where(
            UserVacancies.user_id == user_id).where(UserVacancies.experience == experience)
        result = await session.execute(query)
        await session.commit()
        salaries = []
        for i in result:
            salary = literal_eval(i[0])
            if salary['from'] != None and salary['to'] == None and salary['currency'] == 'RUR':
                if int(salary['from']) % 10 == 0:
                    salaries.append(int(int(salary['from'])))
                else:
                    salaries.append(int(math.ceil(int(salary['from']) / 10) * 10))
            else:
                if salary['from'] != None and salary['to'] == None and salary['currency'] != 'RUR':
                    if (int(salary['from']) * 90) % 10 == 0:
                        salaries.append(int(int(salary['from']) * 90))
                    else:
                        salaries.append(int(math.ceil(int(salary['from']) * 90 / 10) * 10))
            if salary['from'] == None and salary['to'] != None and salary['currency'] == 'RUR':
                if int(salary['to']) % 10 == 0:
                    salaries.append(int(int(salary['to']) * 0.8))
                else:
                    salaries.append(int((math.ceil(int(salary['to']) / 10) * 10) * 0.8))
            else:
                if salary['from'] == None and salary['to'] != None and salary['currency'] != 'RUR':
                    if int(salary['to']) * 90 % 10 == 0:
                        salaries.append(int(int(salary['to']) * 90 * 0.8))
                    else:
                        salaries.append(int((math.ceil(int(salary['to']) * 90 / 10) * 10) * 0.8))
            if salary['from'] != None and salary['to'] != None and salary['currency'] == 'RUR':
                if ((int(salary['from']) + int(salary['to'])) / 2) % 10 == 0:
                    salaries.append(int((int(salary['from']) + int(salary['to'])) / 2))
                else:
                    salaries.append(int(math.ceil(((int(salary['from']) + int(salary['to'])) / 2) / 10) * 10))
            else:
                if salary['from'] != None and salary['to'] != None and salary['currency'] != 'RUR':
                    if ((int(salary['from']) + int(salary['to'])) / 2 * 90) % 10 == 0:
                        salaries.append(int((int(salary['from']) + int(salary['to'])) / 2 * 90))
                    else:
                        salaries.append(int(math.ceil(((int(salary['from']) + int(salary['to'])) / 2 * 90) / 10) * 10))
        set_salaries = sorted(list(set(salaries)))
        salary_dict = {}
        for i in set_salaries:
            salary_dict[i] = salaries.count(i)
        return salary_dict


async def insert_token(user_id, code):
    async with async_session() as session:
        await session.execute(update(Users).where(Users.id == int(user_id)).values(token=code))
        await session.commit()
