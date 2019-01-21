#!/usr/bin/env python3
"""
This module give to program choise tree and meny depend on user access.

.create_list(cls, accesse, options_list) - create menues for different users.

.get_sub_menu()

.get_menu_dict() - get current menu dict.
"""

from interkamen_career.modules.administration.logger_cfg import Logs
from interkamen_career.modules.administration.users import Users

from interkamen_career.modules.support_modules.emailed import EmailSender
from interkamen_career.modules.support_modules.reminder import Reminder
from interkamen_career.modules.support_modules.news import News

from interkamen_career.modules.workers_module import AllWorkers
from interkamen_career.modules.main_career_report import Reports
from interkamen_career.modules.report_analysis import ReportAnalysis
from interkamen_career.modules.drill_instrument_report import DrillInstruments
from interkamen_career.modules.mechanic_report import MechReports
from interkamen_career.modules.rating import Rating
from interkamen_career.modules.drill_passports import DrillPassports
from interkamen_career.modules.work_calendar import WorkCalendars
from interkamen_career.modules.career_status import Statuses
from interkamen_career.modules.workers_salary import WorkersSalary


class Accesse:
    """
    Give to program 'choise tree' and 'meny' depend on user access.
    """

    __slots__ = [
        'menu_list',
        'menu_options',
        'sub_menus',
        'sub_standart_options',
    ]

    def __init__(self, accesse='mechanic'):

        self.menu_options = {
            'info': {
                '--> [Статистика_ремонтов]': 'sub-menu',
                '--> [Статистика_добычи]': 'sub-menu',
            },
            'basic': {
                'Телефоны работников':
                lambda user: AllWorkers(user).print_telefon_numbers(),
                'Календарь пересменок':
                lambda user: WorkCalendars(user).show_year_shifts(),
                'Поменять пароль':
                lambda user: Users(user).change_password(user),
                'Показать новости':
                lambda user: News(user).show_actual_news(),
                'Состояние карьера':
                lambda user: Statuses(user).show_status(),
                '\033[93mВыйти из программы\033[0m': 'exit program',
            },
            'mechanic': {
                '--> [Статистика_ремонтов]': 'sub-menu',
                'Ежедневный отчет механика':
                lambda user: Statuses(user).create_career_status(),
                'Создать отчет по ремонтам':
                lambda user: MechReports(user).create_report(),
                'Редактировать отчет\n------------------------------':
                lambda user: MechReports(user).edit_report(),
                'Календарь обслуживания\n------------------------------':
                lambda user: MechReports(user).maintenance_calendar(),
            },
            'master': {
                '--> [Статистика_добычи]': 'sub-menu',
                'Создать табель добычной бригады':
                lambda user: Reports(user).create_report(),
                'Редактировать табель\n------------------------------':
                lambda user: Reports(user).edit_report(),
                'Создать буровой паспорт':
                lambda user: DrillPassports(user).create_drill_passport(),
                'Редактировать буровой паспорт\n------------------------------':
                lambda user: DrillPassports(user).edit_passport(),
                'Создать отчет по буровым инструментам':
                lambda user: DrillInstruments(user).create_drill_report(),
                'Поставить рейтинг бригаде':
                lambda user: Rating(user).give_rating(),
                'Ежедневный отчет мастера\n------------------------------':
                lambda user: Statuses(user).create_career_status(),
            },
            'boss': {
                '--> [Работники] ': 'sub-menu',
                '--> [Финансы]': 'sub-menu',
                '--> [Меню_механика]': 'sub-menu',
                '--> [Меню_мастера]': 'sub-menu',
                'изменить ежедневный отчет':
                lambda user: Statuses(user).create_career_status(),
            },
            'admin': {'\033[91m--> [administration]\033[0m': 'sub-menu'}
        }

        self.sub_menus = {
            '\033[91m--> [administration]\033[0m': {
                '\033[91m--> [log_menu] \033[0m': 'sub-menu',
                '\033[91m--> [users_menu] \033[0m': 'sub-menu',
                '\033[91m--> [databases] \033[0m': 'sub-menu',
                '\033[91m--> [reminds] \033[0m': 'sub-menu',
                '\033[91mmake backup now\033[0m':
                lambda user: EmailSender(user).make_backup(),
                '\033[91mmain email settings\033[0m':
                lambda user: EmailSender(user).edit_main_propeties(),
                '\033[91mcareer report recivers\033[0m':
                lambda user: EmailSender(user).edit_career_status_recivers(),
            },
            '\033[91m--> [reminds] \033[0m': {
                '\033[91mcreate reminder\033[0m':
                lambda user: Reminder(user).make_custom_remind(),
                '\033[91mshow all reminds\033[0m':
                lambda user: Reminder(user).show_all_reminds(),
            },
            '\033[91m--> [log_menu] \033[0m': {
                'search in logs':
                lambda user: Logs().search_in_logs(),
                'delete all logs':
                lambda user: Logs().delete_all_logs(),
                'show all logs':
                lambda user: Logs().show_logs(),
            },
            '\033[91m--> [users_menu] \033[0m': {
                'create new user':
                lambda user: Users(user).create_new_user(),
                'edit user':
                lambda user: Users(user).edit_user(),
                'show all users':
                lambda user: Users(user).show_all_users(),
            },
            '--> [Работники] ': {
                'Новый работник':
                lambda user: AllWorkers(user).add_new_worker(),
                'Показать работников подразделения':
                lambda user: AllWorkers(user).print_workers_from_division(),
                'Показать уволеных работников':
                lambda user: AllWorkers(user).print_archive_workers(),
                'Вернуть работника из архива':
                lambda user: AllWorkers(user).return_from_archive(),
                'Редактировать работника':
                lambda user: AllWorkers(user).edit_worker(),
                'Показать юбиляров этого года':
                lambda user: AllWorkers(user).show_anniversary_workers(),
                'Создать календарь пересменок':
                lambda user: WorkCalendars(user).create_calendar(),
            },
            '\033[91m--> [databases] \033[0m': {
                'upd company structure':
                lambda user: AllWorkers(user).upd_comp_structure(),
                'print company structure':
                lambda user: AllWorkers(user).print_comp_structure(),
            },
            '--> [Финансы]': {
                'Наряд бригады':
                lambda user: Reports(user).choose_main_report(),
                'Сформировать итог по рейтингу':
                lambda user: Rating(user).count_brigade_winner(),
                'Редактировать список окладов':
                lambda user: WorkersSalary(user).manage_salary_list(),
                'Бригадиры, окладники, бурильщики':
                lambda user: Reports(user).choose_salary_or_drillers(),
            },
            '--> [Меню_механика]': self.menu_options['mechanic'],
            '--> [Меню_мастера]': self.menu_options['master'],
            '--> [Статистика_ремонтов]': {
                'Показать статистику КТГ и КТИ':
                lambda user: MechReports(user).show_statistic(),
                'Статистика по причинам простоев':
                lambda user: MechReports(user).show_statistic(True),
            },
            '--> [Статистика_добычи]': {
                'Статистика добычи по кубатуре':
                lambda user: ReportAnalysis(user).result_analysis(),
                'Статистика по горной массе':
                lambda user: ReportAnalysis(user).rock_mass_analysis(),
                'Статистика по буровому инструменту':
                lambda user: DrillInstruments(user).show_statistic_by_year(),
            }
        }

        self.sub_standart_options = {
            '<-- [Предыдущее меню]': 'menu before',
            '\033[93mВыйти из программы\033[0m': 'exit program',
        }

        self.menu_list = self.create_list(accesse, self.menu_options)

    @classmethod
    def create_list(cls, accesse, options_list):
        """Create accesse and options menus"""
        for name in ('mechanic', 'master', 'boss', 'info'):
            options_list[name].update(options_list['basic'])
        options_list['admin'].update(options_list['boss'])
        return options_list[accesse]

    def get_sub_menu(self, sub_menu_name):
        """Return sub-menu"""
        self.sub_menus[sub_menu_name].update(self.sub_standart_options)
        return self.sub_menus[sub_menu_name]

    def get_menu_dict(self):
        """Give menu dict"""
        return self.menu_list
