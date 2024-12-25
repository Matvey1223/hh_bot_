from database import requests1 as db
from ast import literal_eval

class DataProcessor():
    def __init__(self, all_vacancies, user_id):
        self.all_vacancies = all_vacancies
        self.user_id = user_id

    async def filtered_by_salary(self):
        filters = await db.select_filters(self.user_id)
        filters = filters[0][1:]
        filtered_salary = []
        if '-' not in filters[0]:
            for i in self.all_vacancies:
                if i[1] == 'None':
                    filtered_salary.append(i)
                else:
                    salary = literal_eval(i[1])
                    if salary['from'] == None:
                        filtered_salary.append(i)
                    elif '-' not in filters[0] and int(salary['from']) <= int(filters[0]):
                        filtered_salary.append(i)
        else:
            for i in self.all_vacancies:
                if i[1] == 'None':
                    filtered_salary.append(i)
                else:
                    salary = literal_eval(i[1])
                    if salary['from'] == None or salary['to'] == None:
                        filtered_salary.append(i)
                    else:
                        if (int(salary['from']) <= int(filters[0].split('-')[0])) and (int(salary['to']) >= int(filters[0].split('-')[0])):
                            filtered_salary.append(i)
        return filtered_salary

    async def all_prof_roles(self):
        prof_roles = []
        for i in self.all_vacancies:
            if len(i[6]) > 40:
                pass
            else:
                prof_roles.append(i[6])
        return list(set(prof_roles))


    async def filtered_by_area(self):
        filters = await db.select_filters(self.user_id)
        filters = filters[0][1:]
        filtered_area= []
        for i in self.all_vacancies:
            if filters[1] in i[2]:
                filtered_area.append(i)
        return filtered_area

    async def filtered_by_schedule(self):
        filters = await db.select_filters(self.user_id)
        filters = filters[0][1:]
        filtered_shedule = []
        if filters[2] == 'Пропустить':
            return self.all_vacancies
        for i in self.all_vacancies:
            if i[3] == filters[2]:
                filtered_shedule.append(i)
        return filtered_shedule

    async def filtered_by_experience(self):
        filters = await db.select_filters(self.user_id)
        filters = filters[0][1:]
        filtered_experience = []
        for i in self.all_vacancies:
            if i[4] == filters[3]:
                filtered_experience.append(i)
        return filtered_experience

    async def filetered_by_test(self):
        filters = await db.select_filters(self.user_id)
        filters = filters[0][1:]
        filtered_test = []
        print(filters)
        if filters[5] == '[]':
            return self.all_vacancies
        for i in self.all_vacancies:
            if i[5] == (not bool(filters[5])):
                filtered_test.append(i)
        return filtered_test

    async def filetered_by_role(self):
        filters = await db.select_filters(self.user_id)
        filters = filters[0][1:]
        prof_roles = filters[4].split(',')
        roles_ = []
        for i in prof_roles:
            if '  ' in i :
                roles_.append(i.replace('  ', ', '))
            else:
                roles_.append(i)
        filtered_role = []
        if filters[4] == 'Пропустить':
            return self.all_vacancies
        for i in self.all_vacancies:
            if i[6] in roles_:
                filtered_role.append(i)
        return filtered_role


class SavedSearchFiltered():
    def __init__(self, all_vacancies, user_id, number_filter):
        self.all_vacancies = all_vacancies
        self.user_id = user_id
        self.nubmer_filter = number_filter

    async def filtered_by_salary(self):
        filters = await db.manage_filter_logs(self.user_id, True)
        filters = filters[int(self.nubmer_filter) - 1]
        filters = filters[1:]
        filtered_salary = []
        if '-' not in filters[0]:
            for i in self.all_vacancies:
                if i[1] == 'None':
                    filtered_salary.append(i)
                else:
                    salary = literal_eval(i[1])
                    if salary['from'] == None:
                        filtered_salary.append(i)
                    elif '-' not in filters[0] and int(salary['from']) <= int(filters[0]):
                        filtered_salary.append(i)
        else:
            for i in self.all_vacancies:
                if i[1] == 'None':
                    filtered_salary.append(i)
                else:
                    salary = literal_eval(i[1])
                    if salary['from'] == None or salary['to'] == None:
                        filtered_salary.append(i)
                    else:
                        if (int(salary['from']) <= int(filters[0].split('-')[0])) and (int(salary['to']) >= int(filters[0].split('-')[0])):
                            filtered_salary.append(i)
        return filtered_salary

    async def all_prof_roles(self):
        prof_roles = []
        for i in self.all_vacancies:
            if len(i[6]) > 40:
                pass
            else:
                prof_roles.append(i[6])
        return list(set(prof_roles))

    async def filtered_by_area(self):
        filters = await db.manage_filter_logs(self.user_id, True)
        filters = filters[int(self.nubmer_filter) - 1]
        filtered_area= []
        filters = filters[1:]
        for i in self.all_vacancies:
            if filters[1] in i[2]:
                filtered_area.append(i)
        return filtered_area

    async def filtered_by_schedule(self):
        filters = await db.manage_filter_logs(self.user_id, True)
        filters = filters[int(self.nubmer_filter) - 1]
        filtered_shedule = []
        filters = filters[1:]
        if filters[2] == 'Пропустить':
            return self.all_vacancies
        for i in self.all_vacancies:
            if i[3] == filters[2]:
                filtered_shedule.append(i)
        return filtered_shedule

    async def filtered_by_experience(self):
        filters = await db.manage_filter_logs(self.user_id, True)
        filters = filters[int(self.nubmer_filter) - 1]
        filters = filters[1:]
        filtered_experience = []
        for i in self.all_vacancies:
            if i[4] == filters[3]:
                filtered_experience.append(i)
        return filtered_experience

    async def filetered_by_test(self):
        filters = await db.manage_filter_logs(self.user_id, True)
        filters = filters[int(self.nubmer_filter) - 1]
        filters = filters[1:]
        filtered_test = []
        if filters[5] == '[]':
            return self.all_vacancies
        for i in self.all_vacancies:
            if i[5] == (not bool(filters[4])):
                filtered_test.append(i)
        return filtered_test

    async def filetered_by_role(self):
        filters = await db.manage_filter_logs(self.user_id, True)
        filters = filters[int(self.nubmer_filter) - 1]
        filters = filters[1:]
        filtered_role = []
        if filters[5] == 'Пропустить':
            return self.all_vacancies
        for i in self.all_vacancies:
            if i[6] in filters[5].split(',') and filters[5] != '':
                filtered_role.append(i)
        return filtered_role

