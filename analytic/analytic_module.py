import matplotlib.pyplot as plt
from database import requests1 as db
import numpy as np



class Analytic():
    def __init__(self, id):
        self.id = id

    async def show_vacs_by_experience(self):
        count_vacs = await db.select_all_vacs_by_experience(self.id)
        categories = ['Нет опыта', 'От 1 года до 3 лет', 'От 3 до 6 лет', 'Более 6 лет']
        vacancies = [count_vacs[0], count_vacs[1], count_vacs[2], count_vacs[3]]
        colors_pie = ['blue', 'orange', 'green', 'red']

        # Creating a bar plot for the number of vacancies in the context of experience
        plt.figure(figsize=(14, 7))

        # Bar plot
        plt.subplot(1, 2, 1)
        bars = plt.bar(categories, vacancies, color=colors_pie)
        plt.title('Number of vacancies in the context of experience')
        plt.xlabel('Experience')
        plt.ylabel('Count')
        plt.ylim(0, 10000)  # to match the scale in the user's image

        # Adding the data labels on the bar plot
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, yval + 10, yval, ha='center', va='bottom')

        # Pie chart
        plt.subplot(1, 2, 2)
        explode = (0.1, 0, 0, 0)  # only "explode" the 1st slice (Junior no experience)
        plt.pie(vacancies, explode=explode, labels=categories, autopct='%1.1f%%', colors=colors_pie, startangle=140)

        plt.tight_layout()
        return plt.savefig(f'analytic/result/1_{self.id}'
                           f'')

    async def show_graphic_by_city(self):
        cities = await db.top_5_cities(self.id)
        junior = await db.select_exp_for_top_cities(self.id, cities, 'Нет опыта') # Placeholder values
        junior_plus = await db.select_exp_for_top_cities(self.id, cities, 'От 1 года до 3 лет') # Placeholder values
        middle = await db.select_exp_for_top_cities(self.id, cities, 'От 3 до 6 лет')# Placeholder values
        senior = await db.select_exp_for_top_cities(self.id, cities, 'Более 6 лет') # Placeholder values
        # Using the colors from the previous chart provided by the user
        colors = ['#FFA07A', '#20B2AA', '#8A2BE2', '#F08080']

        # Stacked bar chart
        plt.figure(figsize=(10, 7))

        # Bottom position for each stack
        junior_plus_bottom = [j + jp for j, jp in zip(junior, junior_plus)]
        middle_bottom = [jp + m for jp, m in zip(junior_plus_bottom, middle)]
        senior_bottom = [m + s for m, s in zip(middle_bottom, senior)]

        # Creating the stacked bars
        plt.bar(cities, junior, color=colors[0], label='Junior (no experience)')
        plt.bar(cities, junior_plus, bottom=junior, color=colors[1], label='Junior+ (1-3 years)')
        plt.bar(cities, middle, bottom=junior_plus_bottom, color=colors[2], label='Middle (3-6 years)')
        plt.bar(cities, senior, bottom=middle_bottom, color=colors[3], label='Senior (6+ years)')

        # Adding labels and title
        plt.title('Top 5 Cities with Vacancies')
        plt.xlabel('Cities')
        plt.ylabel('Number of Vacancies')
        plt.legend()

        # Display the chart
        plt.tight_layout()
        return plt.savefig(f'analytic/result/2_{self.id}')

    async def with_or_no_salary_diagramm(self):
        values = await db.with_no_salaries(self.id)
        no_s = values[0]
        with_s = values[1]
        labels = 'With Salary', 'Without Salary'
        sizes = [with_s, no_s]
        colors = ['#1f77b4', '#ff7f0e']

        plt.figure(figsize=(8, 6))
        plt.pie(sizes, colors=colors, autopct='%1.1f%%', startangle=140)

        # Draw the legend with colored labels
        plt.legend(labels, loc="upper right", bbox_to_anchor=(1, 1), title="Legend", frameon=False)

        # Equal aspect ratio ensures that pie is drawn as a circle and title placement
        plt.axis('equal')
        plt.title('Share of vacancies with a specified salary')
        return plt.savefig(f'analytic/result/3_{self.id}')

    async def show_top_10_companies(self):
        companies = await db.top_10_companies(self.id)
        junior_no_exp = await db.exp_top_10_companies(self.id, companies, 'Нет опыта')
        junior_exp = await db.exp_top_10_companies(self.id, companies, 'От 1 года до 3 лет')
        middle_exp = await db.exp_top_10_companies(self.id, companies, 'От 3 до 6 лет')
        senior_exp = await db.exp_top_10_companies(self.id, companies, 'Более 6 лет')

        bar_width = 0.85
        index = np.arange(len(companies))

        # Plotting data
        fig, ax = plt.subplots(figsize=(15, 8))
        bar1 = plt.bar(index, junior_no_exp, bar_width, label='Junior (no experience)', color='blue')
        bar2 = plt.bar(index, junior_exp, bar_width, label='Junior (1-3 years)', color='orange', bottom=junior_no_exp)
        bar3 = plt.bar(index, middle_exp, bar_width, label='Middle (3-6 years)', color='green',
                       bottom=np.add(junior_no_exp, junior_exp))
        bar4 = plt.bar(index, senior_exp, bar_width, label='Senior (6+ years)', color='red',
                       bottom=np.add(np.add(junior_no_exp, junior_exp), middle_exp))

        plt.xlabel('Employer')
        plt.ylabel('Number of Vacancies')
        plt.title('Top 10 hunt companies')
        plt.xticks(index, companies, rotation=30)
        plt.legend()

        # Show the plot
        return plt.savefig(f'analytic/result/4_{self.id}')

    async def show_shedule(self):
        schedules = ['Удаленная работа', 'Полный день', 'Гибкий график', 'Сменный график', 'Вахтовый метод']
        experiences = ['Нет опыта', 'От 1 года до 3 лет', 'От 3 до 6 лет', 'Более 6 лет']
        junior_no_exp = await db.schedule_exps(self.id, schedules, experiences[0])
        junior_exp = await db.schedule_exps(self.id, schedules, experiences[1])
        middle_exp = await db.schedule_exps(self.id, schedules, experiences[2])
        senior_exp = await db.schedule_exps(self.id, schedules, experiences[3])

        # We will stack these on top of each other, so we need to cumulatively add the previous values as the bottom parameter
        cum_junior_no_exp = np.array(junior_no_exp)
        cum_junior_exp = cum_junior_no_exp + np.array(junior_exp)
        cum_middle_exp = cum_junior_exp + np.array(middle_exp)

        # Create the bar chart
        fig, ax = plt.subplots(figsize=(15, 8))

        ax.bar(schedules, junior_no_exp, label='Junior (no experience)', color='blue')
        ax.bar(schedules, junior_exp, label='Junior (1-3 years)', color='orange', bottom=junior_no_exp)
        ax.bar(schedules, middle_exp, label='Middle (3-6 years)', color='green', bottom=cum_junior_exp)
        ax.bar(schedules, senior_exp, label='Senior (6+ years)', color='red', bottom=cum_middle_exp)

        # Adding labels and title
        plt.xlabel('Schedule')
        plt.ylabel('Number of Vacancies')
        plt.title('Distribution of Vacancies by Work Schedule')
        plt.legend()

        # Show the plot
        return plt.savefig(f'analytic/result/5_{self.id}')

    async def show_employment(self):
        employments = ['Полная занятость', 'Частичная занятость', 'Проектная работа', 'Волонтерство', 'Стажировка']
        experiences = ['Нет опыта', 'От 1 года до 3 лет', 'От 3 до 6 лет', 'Более 6 лет']
        junior_no_exp = await db.employment_analytic(self.id, employments, experiences[0])
        junior_exp = await db.employment_analytic(self.id, employments, experiences[1])
        middle_exp = await db.employment_analytic(self.id, employments, experiences[2])
        senior_exp = await db.employment_analytic(self.id, employments, experiences[3])

        # We will stack these on top of each other, so we need to cumulatively add the previous values as the bottom parameter
        cum_junior_no_exp = np.array(junior_no_exp)
        cum_junior_exp = cum_junior_no_exp + np.array(junior_exp)
        cum_middle_exp = cum_junior_exp + np.array(middle_exp)

        # Create the bar chart
        fig, ax = plt.subplots(figsize=(15, 8))

        ax.bar(employments, junior_no_exp, label='Junior (no experience)', color='blue')
        ax.bar(employments, junior_exp, label='Junior (1-3 years)', color='orange', bottom=junior_no_exp)
        ax.bar(employments, middle_exp, label='Middle (3-6 years)', color='green', bottom=cum_junior_exp)
        ax.bar(employments, senior_exp, label='Senior (6+ years)', color='red', bottom=cum_middle_exp)

        # Adding labels and title
        plt.xlabel('Schedule')
        plt.ylabel('Number of Vacancies')
        plt.title('Distribution of Vacancies by Work Schedule')
        plt.legend()

        # Show the plot
        return plt.savefig(f'analytic/result/6_{self.id}')

    async def top_10_prof_roles(self):
        roles = await db.top_10_prof_roles(self.id)
        # Sample distribution across experience levels for each role
        # The values are randomly generated for the example purpose

        junior_values = await db.show_prof_roles_analytic(self.id, roles, 'Нет опыта')
        middle_values = await db.show_prof_roles_analytic(self.id, roles, 'От 1 года до 3 лет')
        senior_values = await db.show_prof_roles_analytic(self.id, roles, 'От 3 до 6 лет')
        no_experience_values = await db.show_prof_roles_analytic(self.id, roles, 'Более 6 лет')
        titles = ['Нет опыта', 'От 1 года до 3 лет', 'От 3 до 6 лет', 'Более 6 лет']

        # Now plotting again with the corrected data for the 'no experience' category
        fig, axs = plt.subplots(2, 2, figsize=(15, 8), sharey=True)
        axs = axs.flatten()  # Flatten to 1D array for easy iteration

        # Plot each set of data with the corrected 'no experience' values
        for i, (values, title) in enumerate(zip([no_experience_values, junior_values, middle_values, senior_values], titles)):
            axs[i].barh(roles, values, color='skyblue')
            axs[i].set_title(title)
            axs[i].invert_yaxis()  # Invert y-axis so the roles are in descending order

        plt.tight_layout()

        return plt.savefig(f'analytic/result/7_{self.id}')

    def calculate_xticks(self, data):
        min_val = min(data.keys())
        max_val = max(data.keys())
        step = (max_val - min_val) / 10  # Dynamic step based on range
        return list(range(int(min_val), int(max_val) + int(step), int(step)))
    async def salaries_analytic(self):
        titles = ['Нет опыта', 'От 1 года до 3 лет', 'От 3 до 6 лет', 'Более 6 лет']
        data_no_experience = await db.salaries_analytic(self.id, titles[0])
        data_1_to_3_years = await db.salaries_analytic(self.id, titles[1])
        data_3_to_6_years = await db.salaries_analytic(self.id, titles[2])
        data_more_than_6_years = await db.salaries_analytic(self.id, titles[3])

        plt.figure(figsize=(20, 15))

        # Plot for "No Experience"
        plt.subplot(2, 2, 1)
        plt.plot(data_no_experience.keys(), data_no_experience.values())
        plt.title('No Experience')
        plt.xlabel('Salary')
        plt.ylabel('Count')
        plt.xticks(self.calculate_xticks(data_no_experience))
        plt.grid(True)

        # Plot for "1 to 3 Years"
        plt.subplot(2, 2, 2)
        plt.plot(data_1_to_3_years.keys(), data_1_to_3_years.values(), color='orange')
        plt.title('1 to 3 Years')
        plt.xlabel('Salary')
        plt.ylabel('Count')
        plt.xticks(self.calculate_xticks(data_1_to_3_years))
        plt.grid(True)

        # Plot for "3 to 6 Years"
        plt.subplot(2, 2, 3)
        plt.plot(data_3_to_6_years.keys(), data_3_to_6_years.values(), color='green')
        plt.title('3 to 6 Years')
        plt.xlabel('Salary')
        plt.ylabel('Count')
        plt.xticks(self.calculate_xticks(data_3_to_6_years))
        plt.grid(True)

        # Plot for "More Than 6 Years"
        plt.subplot(2, 2, 4)
        plt.plot(data_more_than_6_years.keys(), data_more_than_6_years.values(), color='red')
        plt.title('More Than 6 Years')
        plt.xlabel('Salary')
        plt.ylabel('Count')
        plt.xticks(self.calculate_xticks(data_more_than_6_years))
        plt.grid(True)

        plt.tight_layout()
        return plt.savefig(f'analytic/result/8_{self.id}')




