#!/usr/bin/env python3
"""
Everyday career status.

.create_career_status() - create career status report from different users
(master and mechanic)

.show_status() - show career status.
"""

from threading import Thread
from itertools import zip_longest
from datetime import date, timedelta
from .support_modules.emailed import EmailSender
from .work_calendar import WorkCalendars
from .workers_module import AllWorkers
from .main_career_report import Reports
from .administration.logger_cfg import Logs
from .drill_passports import DrillPassports
from .support_modules.custom_exceptions import MainMenu
from .support_modules.standart_functions import (
    BasicFunctionsS
    as BasF_S
)


LOGGER = Logs().give_logger(__name__)

class CareerStatusS(BasF_S):
    """Current career status."""

    __slots__ = [
        'date',
        'cur',
        'itr_list',
        'mach',
        'storage',
        'works_plan',
        'res',
        'date_numbers',
        'user'
    ]

    def __init__(self, user):
        self.user = user
        self.date = {
            "today": str(date.today()),
            "tomorrow": str(date.today() + timedelta(days=1)),
        }
        self.date_numbers = list(map(int, self.date['today'].split('-')))
        self.cur = {
            "brig":
            WorkCalendars(user).give_current_brigade(self.date_numbers),
            "itr":
            WorkCalendars(user).give_current_itr(
                list(map(int, self.date['tomorrow'].split('-')))
            ),
            'month_shifts':
            WorkCalendars(user).give_current_month_shifts(self.date_numbers),
        }
        self.itr_list = AllWorkers(user).print_telefon_numbers(
            itr_shift=self.cur["itr"])
        self.mach = {
            "to_repare": None,
            "to_work": None,
        }
        self.storage = {
            "KOTC": None,
            "sale": None,
        }
        self.works_plan = {
            "expl_work": [],
            "rock_work": [],
        }
        self.res = {
            "month": None,
            "shift": None,
        }
        self.add_info(user)

    def __repr__(self):
        """Print status."""
        output = (
            f"\n\033[7mCостояние карьера на вечер: {self.date['today']}\033[0m"
            "\n\n\033[4mРаботники:\033[0m"
            f"\nСейчас на смене: {self.cur['brig']}"
            f"\nСмена ИТР: {self.cur['itr']}"
            "\nРаботники ИТР:\n"
        )

        itr_list = []
        for worker in self.itr_list:
            itr_list.append("{:<15}- {:<24}тел.: {}".format(*worker))
        itr_list = '\n'.join(itr_list)

        output += itr_list
        output += (
            "\n\n\033[4mДобыто блок-заготовок:\033[0m"
            f"\n\tв текущем месяце: {self.res['month']} м.куб."
            f"\n\tтекущей вахтой: {self.res['shift']} м.куб."
            "\n\n\033[4mОбъем блоков на отгрузочном складе:\033[0m"
            f"\n\tЦеховой камень: {self.storage['KOTC']} м.куб."
            f"\n\tСторонний камень: {self.storage['sale']} м.куб."
            "\n\n\033[4mСостояние техники:\033[0m"
            "\n\t\033[91mВыведена на ремонт:\033[0m\n\t"
        )
        output += f'{self.mach["to_repare"]}'
        output += "\n\t\033[92mВведена в работу:\033[0m\n\t"
        output += f'{self.mach["to_work"]}'
        output += (
            f"\n\n\033[4mПлан работ на {self.date['tomorrow']}\033[0m"
            "\n\t\tВзрывные работы."
            "\n\tгоризонт  направление  качество  квадрант\n\t"
        )
        output += f"{self._format_works_list('expl_work')}"
        output += (
            "\n\n\t\tДобычные работы."
            "\n\tгоризонт  направление  качество  квадрант\n\t"
        )
        output += f"{self._format_works_list('rock_work')}"
        output = output.replace(
            'None', '\033[91m<Информация отсутствует>\033[0m')
        return output

    @classmethod
    def _create_plan_html(cls, works_list):
        """Create HTML table for plan works."""
        try:
            works_list = ['</td><td>'.join((x, y, z, n))
                          for (x, y, z, n) in works_list]
        except ValueError:
            works_list = ['</td><td>'.join(('-', '-', '-', '-'))]
        works_list = '</td></tr><tr align="center"><td>'.join(works_list)
        plan_table = '<tr align="center"><td>' + works_list + '</td></tr>'
        return plan_table

    @classmethod
    def _ready_to_input(cls, title: str):
        """Check if user ready to input."""
        while True:
            ready = input(f"\nЕсли готовы ввести {title}, введите [Y]: ")
            if ready.lower() == 'y':
                break

    def _format_works_list(self, works_kind: str) -> str:
        """Format planed works list to output."""
        work_list = []
        if not self.works_plan[works_kind]:
            work_list = 'Не запланированы.'
        elif self.works_plan[works_kind][0] == 'Не запланированы.':
            work_list = 'Не запланированы.'
        else:
            for direction in self.works_plan[works_kind]:
                work_list.append("{:^10} {:^10} {:^10} {:^10}"
                                 .format(*direction))
            work_list = '\n\t'.join(work_list)
        return work_list

    def _check_tomorrow_passports(self):
        """Check if tomorrow passports exists."""
        tomorrow_passports = (
            DrillPassports(self.user)
            .give_dpassports_for_date(self.date["tomorrow"])
        )
        if not tomorrow_passports:
            print(f"Буровые паспорта за {self.date['tomorrow']}"
                  " число отстутствуют.")
            contin = input("Если желаете продолжить заполнение отчета "
                           "без буровзрывных работ введите 'c': ")
            if contin.lower() not in ['c', 'с']:
                print("Составление отчета отменено.")
                input("[ENTER] - выйти в меню.")
                raise MainMenu
        return tomorrow_passports

    def _add_master_info(self, user_id):
        """Add info from master."""
        tomorrow_passports = self._check_tomorrow_passports()
        self._input_current_result()
        self._input_strage_volume()

        directions = ['восток', 'запад', 'север', 'юг']

        if tomorrow_passports:
            self._ready_to_input('взрывные работы')
            self._expl_works(tomorrow_passports, directions)
        else:
            self.works_plan["expl_work"].append('Не запланированы.')

        self._ready_to_input('добычные работы')
        self._plan_works(directions)

        print("\033[92mОтчет создан.\033[0m")
        LOGGER.warning(f"User '{user_id}' create career status from master")
        input('\n[ENTER] - выйти.')

    def _expl_works(self, tomorrow_passports, directions):
        """Input expl works."""
        super().clear_screen()
        work_list = []
        quol = ['блоки', 'масса']
        print("Введите информацию по \033[4mбуровзрывным работам\033[0m на {}"
              .format(self.date['tomorrow']))
        for passport in tomorrow_passports:
            print(
                "\nПасспорт №{}: Горизонт: '{}' Тип: '{}' "
                .format(int(passport.params.number),
                        str(passport.params.horizond),
                        str(passport.params.massive_type))
            )
            print("Выберете направление:")
            direction = super().choise_from_list(directions)
            print("Выберете предполагаемое качество:")
            quoli = super().choise_from_list(quol)
            coord = input("Введите квадрант: ")
            horizond = str(passport.params.horizond)
            work = (horizond, direction, quoli, coord)
            work_list.append(work)
        self.works_plan["expl_work"] = work_list

    def _plan_works(self, directions):
        """Input rock or expl work"""
        quol = ['разборка', 'пассир.', 'бурение']
        horizonds = ['+108', '+114', '+120', '+126', '+132']
        work_list = []
        work_directions = []
        print_list = ''
        while True:
            super().clear_screen()
            print("Введите информацию по работам на {}"
                  .format(self.date['tomorrow']))
            print("\033[4mДобычные работы:\033[0m")
            print("\tгоризонт  направление  качество  квадрант")
            print('\t' + print_list)
            print("\n[ENTER] - закончить ввод\n"
                  "Добавить работы:")
            print("Выберете горизонт:")
            horizond = super().choise_from_list(horizonds, none_option=True)
            if not horizond:
                break
            print("Выберете направление:")
            direction = super().choise_from_list(directions)
            print("Выберете предполагаемое качество:")
            quoli = super().choise_from_list(quol)
            coord = input("Введите квадрант: ")
            work = (horizond, direction, quoli, coord)
            work_directions.append("{:^10} {:^10} {:^10} {:^10}".format(*work))
            print_list = '\n\t'.join(work_directions)
            work_list.append(work)
        if not work_list:
            work_list.append('Не запланированы.')
        self.works_plan['rock_work'] = work_list

    def _input_strage_volume(self):
        """Add rocks from storage."""
        print("Введите объем склада:")
        self.storage["KOTC"] = super().float_input(msg='Цеховой камень: ')
        self.storage["sale"] = super().float_input(msg='На продажу: ')

    def _input_current_result(self):
        """Add current \result."""
        self.res["shift"] = super().float_input(msg="Введите добычу вахты: ")
        if self.cur["brig"] == 'Бригада 1':
            self.res["month"] = self.res["shift"]
        else:
            shift1_res = Reports(self.user).give_main_results(
                *str(date.today()).split('-')[:-1], 'Смена 1')[1]
            self.res["month"] = (round(shift1_res, 1) + self.res["shift"])

    def _add_mechanic_info(self, user_id):
        """Add info from mechanic."""
        self.mach["to_repare"] = self._create_mach_list(
            title="\033[4mВыберете технику, выведенную в ремонт:\033[0m")
        self.mach["to_work"] = self._create_mach_list(
            title="\033[4mВыберете технику, введенную в работу:\033[0m")
        print("\033[92mОтчет создан.\033[0m")
        LOGGER.warning(f"User '{user_id}' create career status from mechanic")
        input('\n[ENTER] - выйти.')

    def _create_mach_list(self, *, title):
        """Create mach list to repare or from repare."""
        mach_name = [
            'УАЗ-390945', 'УАЗ-220695', 'ГАЗ-3307', 'Commando-110',
            'Commando-120', 'Komazu-WA470', 'Volvo-L150', 'КС-5363А',
            'КС-5363Б', 'КС-5363Б2 ', 'AtlasC-881', 'AtlasC-882',
            'Hitachi-350', 'Hitachi-400', 'КрАЗ-914', 'КрАЗ-413',
            'КрАЗ-069', 'Бул-10', 'ДЭС-AD'
        ]
        mach_list = []
        while True:
            super().clear_screen()
            print(title)
            print(mach_list)
            print("\n[ENTER] - закончить ввод\n"
                  "Выберете технику:")
            mach = super().choise_from_list(mach_name, none_option=True)
            if not mach:
                break
            mach_list.append(mach)
        if not mach_list:
            mach_list.append('Отсутствуют.')
        return mach_list

    def _check_if_report_comlete(self, name):
        """Check mechanics and master data."""
        if self.mach["to_repare"] and self.works_plan["rock_work"]:
            html = self._create_html_status()
            emailed_status = Thread(
                target=self._try_to_emailed_status,
                args=(name, html)
            )
            emailed_status.start()

    def _try_to_emailed_status(self, name: str, html: str):
        """Try to send status via email."""
        message = EmailSender(self.user).email_prop["status message"]
        if name:
            message += f"\nВНИМАНИЕ! {name} внес корректировки в отчет:"
            html = html.replace(
                '>future_correction<',
                f' style="color:red"><b>(Скорректировал - {name})</b><'
            )
        else:
            html = html.replace(
                '>future_correction<',
                '> <'
            )
        unsucsesse = EmailSender(self.user).try_email(
            recivers_adreses="career status recivers",
            message=message,
            subject='Состояние карьера',
            add_html=html,
            html_img=(
                super().get_root_path() / 'support_img' / 'inter_header.png'),
            add_file=super().get_root_path() / 'html_blancs' / 'map.pdf',
        )
        if unsucsesse:
            print(unsucsesse)

    def _create_html_status(self):
        """Create career status in  html."""
        blanc_html = (
            super().get_root_path() / 'html_blancs' / 'career_status.html')
        with open(blanc_html, 'r', encoding='utf-8') as file:
            html = file.read()
        shift_calendar = self._create_shift_calendar()
        mach_table = self._create_mach_html()
        expl_table = self._create_plan_html(self.works_plan['expl_work'])
        rock_table = self._create_plan_html(self.works_plan['rock_work'])
        contact_table = self._create_contact_table()
        html = html.format(
            self.date['today'],
            self.cur['brig'],
            self.cur['itr'],
            round(self.res['month'], 2),
            round(self.res['shift'], 2),
            self.storage['KOTC'],
            self.storage['sale'],
            mach_table,
            self.date['tomorrow'],
            expl_table,
            rock_table,
            shift_calendar,
            contact_table
        )
        return html

    def _create_shift_calendar(self):
        """Create calendar of ITR and brigade shifts."""
        calendar = WorkCalendars(self.user).give_current_month_shifts(
            self.date_numbers,
            cal_format='html',
        )
        tomorrow = self.date['tomorrow'].split('-')[-1]
        tomorrow = str(int(tomorrow))
        calendar = calendar.replace(
            f'>{tomorrow}<',
            f' style="color:red"><b>{tomorrow}</b><',
        )
        return calendar

    def _create_contact_table(self):
        """Create contact table of ITR workers."""
        contact_table = [x + '- ' + y + '<br />тел.: ' + z
                         for (x, y, z) in self.itr_list]
        contact_table = '<br />'.join(contact_table)
        table = '<p>' + contact_table + '</p>'
        return table

    def _create_mach_html(self):
        """Create HTML table from machine list."""
        mach_list = list(zip_longest(
            self.mach["to_repare"],
            self.mach["to_work"],
        ))
        mach_list = ['</td><td>'.join((str(x), str(y)))
                     for (x, y) in mach_list]
        mach_list = '</td></tr><tr align="center"><td>'.join(mach_list)
        mach_list = mach_list.replace('None', '')
        table = '<tr align="center"><td>' + mach_list + '</tr>'
        return table

    def _ask_for_recreate(self):
        """If daily career status already exist and comlate.
        But user want to make changes."""
        super().clear_screen()
        ask = input("Ежедневный отчет уже сформирован и разослан руководству,"
                    "\nВы уверены, что хоти внести корректировки? Y/N: ")
        answer = bool(ask.lower() == 'y')
        return answer

    def _choose_info_to_add(self, user_id):
        """Admin can choose what kind info he want to add."""
        info_type = {
            'master': self._add_master_info,
            'mechanic': self._add_mechanic_info,
        }
        accesse = super().choise_from_list(info_type)
        info_type[accesse](user_id)
        super().clear_screen()

    def add_info(self, user):
        """Add info depend on user access."""
        answer = True
        name = None
        if self.mach["to_repare"] and self.works_plan["rock_work"]:
            answer = self._ask_for_recreate()
            name = super().make_name_short(user.name)
        if answer:
            info_type = {
                'master': self._add_master_info,
                'mechanic': self._add_mechanic_info,
                'admin': self._choose_info_to_add,
                'boss': self._choose_info_to_add,
            }
            info_type[user.accesse](user.login)
            self._check_if_report_comlete(name)
        else:
            print("\033[91mВы отменили изменение отчета.\033[0m")
            input('\n[ENTER] - выйти.')

    def give_shift_calendar(self):
        """Return shifts calendar."""
        output = "\n\n\033[4mПересменки в этом месяце:\033[0m\n\t"
        output += (
            self.cur['month_shifts']
            .replace(
                ' ' + self.date['tomorrow'].split('-')[-1],
                ' \033[41m' + self.date['tomorrow'].split('-')[-1] + '\033[0m'
            )
        )
        return output


class Statuses(BasF_S):
    """Create and save curent status reports."""

    __slots__ = [
        'car_stat_path',
        'car_stat_file',
        'user',
    ]

    def __init__(self, user):
        self.car_stat_path = super().get_root_path() / 'data' / 'carer_status'
        self.user = user
        if self.car_stat_path.exists():
            self.car_stat_file = super().load_data(
                data_path=self.car_stat_path,
                user=user,
            )
        else:
            self.car_stat_file = {}
            super().dump_data(
                data_path=self.car_stat_path,
                base_to_dump=self.car_stat_file,
                user=user,
            )

    def create_career_status(self):
        """Create status if not exist."""
        if str(date.today()) in self.car_stat_file:
            self.car_stat_file[str(date.today())].add_info(self.user)
        else:
            self.car_stat_file[str(date.today())] = CareerStatusS(self.user)
        super().dump_data(
            data_path=self.car_stat_path,
            base_to_dump=self.car_stat_file,
            user=self.user,
        )

    def show_status(self):
        """Show career status."""
        status = None
        if self.car_stat_file:
            status = sorted(self.car_stat_file)[-1]
        if status:
            super().clear_screen()
            print(self.car_stat_file[status])
            calendar = input("\n[k] - показать календарь пересменок.\n"
                             "[ENTER] - выйти: ")
            if calendar.lower() in ['k', 'к']:
                print(self.car_stat_file[status].give_shift_calendar())
                input('\n[ENTER] - выйти.')
        else:
            print("Ежедневные отчеты отсутствуют.")
