#!/usr/bin/env python3
"""
Main career report.
This module for create main career report by 'master' and complate it by 'boss'
users.
It can count worker salary and compilate statistic of brigades results.

class MainReportS:

.unofficial_workers() - return list of unofficial workers.

.count_result() - count totall result for brigade stones.

.count_rock_mass() - count totall result for brigade rock mass.

.count_all_workers_in_report() - count sallary for all workers in report.

.create_ktu_list() - create list of workers KTU.

.coutn_delta_ktu() - add delta KTU for worker.

class Reports:

.choose_salary_or_drillers() - edit drillers or sallary workers list.

.give_main_results() - return brigade drill meters, result and rock_mass.

.give_avaliable_to_edit() - give reports that avaliable to edit

.create_report() - create new main report.

.edit_report() - edition uncompleted report by user with 'master' accesse.

.choose_main_report() - choose main report by year.
"""

from threading import Thread
from typing import List, Dict
from pprint import pprint
from .workers_module import AllWorkers
from .support_modules.dump_to_exl import DumpToExl
from .support_modules.custom_exceptions import MainMenu
from .administration.logger_cfg import Logs
from .drill_passports import DrillPassports
from .support_modules.emailed import EmailSender
from .support_modules.standart_functions import (
    BasicFunctionsS
    as BasF_S
)


LOGGER = Logs().give_logger(__name__)


class MainReportS(BasF_S):
    """
    Main career report.
    """

    __slots__ = [
        'status',
        'workers_showing',
        'result',
        'bonuses',
        'rock_mass',
        'totall',
    ]

    def __init__(self, status: str, shift: str, date: str):
        self.workers_showing = {
            'бух.': {
                'КТУ': {},
                'часы': {},
                'зарплата': {}
            },
            'факт': {
                'КТУ': {},
                'часы': {},
                'зарплата': {}
            }}
        self.result = {
            'машины второго сорта': 0,
            'шпурометры': 0,
            'категории': {'меньше 0.7': 0,
                          '0.7-1.5': 0,
                          'выше 1.5': 0},
            'погоризонтно': {'+108': 0,
                             '+114': 0,
                             '+120': 0,
                             '+126': 0,
                             '+132': 0}
            }
        self.bonuses = {'более 250 кубов': False,
                        'победа по критериям': False}
        self.rock_mass = {'+108': 0,
                          '+114': 0,
                          '+120': 0,
                          '+126': 0,
                          '+132': 0}
        self.totall = 0
        self.status = {'status': status,
                       'shift': shift,
                       'date': date}
        # Avaliable statuses: '\033[91m[не завершен]\033[0m'
        #                     '\033[93m[в процессе]\033[0m'
        #                     '\033[92m[завершен]\033[0m'

    @classmethod
    def _count_totall(cls, value_list: List):
        """Count totall hours"""
        totall = 0
        for worker in value_list:
            totall += value_list[worker]
        return totall

    @classmethod
    def _colorise_salary_and_drillers(cls, name: str, output: str, user) -> str:
        """Colorise sallary and drillers in report output."""
        if (name in Reports(user).salary_workers or
                name in Reports(user).drillers):
            output = ''.join(['\033[36m', output, '\033[0m'])
        return output

    @classmethod
    def _colorise_brigadiers(cls, name: str, output: str, user) -> str:
        """Colorise sallary and drillers in report output."""
        if name in Reports(user).brigadiers:
            if '\033[36m' in output:
                output = output.replace('\033[36m', '\033[91m')
            else:
                output = ''.join(['\033[91m', output, '\033[0m'])
        return output

    def _add_color_to_repr(self, name, t_output, user):
        """Colorise driller, salary adn brigadiers."""
        t_output = self._colorise_salary_and_drillers(name, t_output, user)
        t_output = self._colorise_brigadiers(name, t_output, user)
        return t_output

    def __repr__(self, user=None):
        """Print main report"""
        output = "\n{date} {shift} {status}".format(**self.status)
        output += ("""\n
машины второго сорта: {0[машины второго сорта]}
шпурометры: {0[шпурометры]}\n""".format(self.result) +
                   """\nкубатура:
меньше 0.7: {0[меньше 0.7]}
0.7-1.5: {0[0.7-1.5]}
выше 1.5: {0[выше 1.5]}\n""".format(self.result['категории']))
        by_horisont = {
            key: value for (key, value) in self.result['погоризонтно'].items()
            if value > 0}
        output += "\nпогоризонтный выход блоков:\n"
        for horizont in by_horisont:
            output += horizont + ': ' + str(by_horisont[horizont]) + '\n'
        if self.status['status'] == '\033[91m[не завершен]\033[0m':
            output += '\n'
            for name in sorted(self.workers_showing['факт']['часы']):
                short_name = super().make_name_short(name)
                output += "{:<14}: {}\n".format(
                    short_name, self.workers_showing['факт']['часы'][name])
            return output
        output += "\nГорная масса:\n"
        for gorizont in sorted(self.rock_mass):
            output += gorizont + ': ' + str(self.rock_mass[gorizont]) + '\n'
        output += '\nСумма к распределению: ' + str(self.totall) + '\n'
        if self.bonuses['более 250 кубов']:
            output += "\033[92m[Премия за 250]\033[0m\n"
        if self.bonuses['победа по критериям']:
            output += "\033[92m[Победа в соц. соревновании]\033[0m\n"
        output += "                   \
Фактические               Бухгалтерские"
        output += "\n    ФИО         часы   КТУ       З/п     |\
 часы   КТУ      З/п\n"
        for name in sorted(self.workers_showing['бух.']['часы']):
            short_name = super().make_name_short(name)
            t_output = (
                "{:<14}: {:>3} | {:>4} | {:<9,}р. | ".format(
                    short_name,
                    self.workers_showing['факт']['часы'][name],
                    self.workers_showing['факт']['КТУ'][name],
                    self.workers_showing['факт']['зарплата'][name],
                )
                + "{:>3} | {:>4} | {:<9,}р.\n".format(
                    self.workers_showing['бух.']['часы'][name],
                    self.workers_showing['бух.']['КТУ'][name],
                    self.workers_showing['бух.']['зарплата'][name]
                )
            )
            if user:
                t_output = self._add_color_to_repr(name, t_output, user)
            output += t_output
        unofficial_workers = self.unofficial_workers()
        for name in unofficial_workers:
            short_name = super().make_name_short(name)
            t_output = "{:<14}: {:>3} | {:>4} | {:<9,}\n".format(
                short_name, self.workers_showing['факт']['часы'][name],
                self.workers_showing['факт']['КТУ'][name],
                self.workers_showing['факт']['зарплата'][name])
            if user:
                t_output = self._add_color_to_repr(name, t_output, user)
            output += t_output
        return output

    def _count_salary(self, direction: str, worker: str, coefficient: float):
        """Count totall salary"""
        self.workers_showing[direction]['зарплата'][worker] = round(
            self.workers_showing[direction]['КТУ'][worker]
            * self.totall * coefficient
            / len(self.workers_showing[direction]['КТУ']), 2)

    def _count_sal_workers_and_drill(self, worker: str, user):
        """Count sallary workers and drillers"""
        oklad = 0
        if worker in Reports(user).salary_workers:
            oklad = (self.workers_showing['факт']['часы'][worker]
                     / 11 * 50000 / 15)
        elif worker in Reports(user).drillers:
            oklad = (self.result['шпурометры'] * 36)
        if self.bonuses['более 250 кубов']:
            oklad += (5000 / 15 / 11
                      * self.workers_showing['факт']['часы'][worker])
        self.workers_showing['факт']['зарплата'][worker] = round(oklad, 2)

    def _add_brigad_bonus(self, worker: str):
        """Add bonus if brigad win monthly challenge"""
        if self.bonuses['победа по критериям']:
            self.workers_showing['факт']['зарплата'][worker] += 3000

    def _add_brigadiers_persent(self, worker: str, direction: str, user):
        """Add persent if worker are brigadier."""
        if worker in Reports(user).brigadiers:
            if direction == 'бух.':
                persent = 1.15
            elif direction == 'факт':
                persent = 1.1
            oklad = (
                self.workers_showing[direction]['зарплата'][worker] * persent
            )
            self.workers_showing[direction]['зарплата'][worker] = round(
                oklad, 2)

    def _add_delta_ktu_to_worker(self, delta: float, direction: str):
        """Add delta ktu to worker"""
        print('\n' + 'КТУ: ' + direction)
        workers_list = self.workers_showing[direction]['КТУ'].items()
        print("\nВыберете работника, которому хотите добавить остаток:")
        worker = super().choise_from_list(workers_list)
        worker_ktu = self.workers_showing[direction]['КТУ'][worker[0]]
        result = round(delta + worker_ktu, 2)
        self.workers_showing[direction]['КТУ'][worker[0]] = result
        print("Остаток добавлен.\n")
        print(direction)
        pprint(self.workers_showing[direction]['КТУ'])

    def unofficial_workers(self) -> List[str]:
        """Return unofficial workers"""
        unofficial_workers = [
            worker
            for worker in self.workers_showing['факт']['часы']
            if worker not in self.workers_showing['бух.']['часы']
        ]
        return unofficial_workers

    def count_result(self):
        """Count totall stone result"""
        result = 0
        for item in self.result['категории']:
            result += self.result['категории'][item]
        if result > 250:
            self.bonuses['более 250 кубов'] = True
        return result

    def count_rock_mass(self) -> float:
        """Count totall rock_mass"""
        result = 0
        for item in self.rock_mass:
            result += self.rock_mass[item]
        return result

    def count_all_workers_in_report(self, user):
        """Apply action to all workers in report"""
        self.count_result()
        for direction in self.workers_showing:
            for worker in self.workers_showing[direction]['КТУ']:
                if ((worker in Reports(user).salary_workers or
                     worker in Reports(user).drillers) and
                        direction == 'факт'):
                    self._count_sal_workers_and_drill(worker, user)
                elif direction == 'бух.':
                    coefficient = 1
                    self._count_salary(direction, worker, coefficient)
                elif direction == 'факт':
                    coefficient = 1.5
                    self._count_salary(direction, worker, coefficient)
                self._add_brigad_bonus(worker)
                self._add_brigadiers_persent(worker, direction, user)

    def create_ktu_list(self):
        """Create ktu list"""
        for direction in self.workers_showing:
            totall_hours = self._count_totall(
                self.workers_showing[direction]['часы'])
            for worker in self.workers_showing[direction]['часы']:
                ktu = (
                    self.workers_showing[direction]['часы'][worker]
                    / totall_hours
                    * len(self.workers_showing[direction]['часы'])
                    )
                self.workers_showing[direction]['КТУ'][worker] = round(ktu, 2)
            self.coutn_delta_ktu(direction)

    def coutn_delta_ktu(self, direction: str):
        """Add delta ktu to worker"""
        totall_ktu = self._count_totall(self.workers_showing[direction]['КТУ'])
        delta_ktu = len(self.workers_showing[direction]['КТУ']) - totall_ktu
        delta_ktu = round(delta_ktu, 2)
        if delta_ktu != 0:
            print(f"\nВ процессе округления образовался остаток: {delta_ktu}")
            self._add_delta_ktu_to_worker(delta_ktu, direction)


class Reports(BasF_S):
    """
    Class to manage with reports.
    """
    __slots__ = [
        'user',
        'data_path',
        'salary_path',
        'drillers_path',
        'brigadiers_path',
        'shifts',
        'salary_workers',
        'drillers',
        'brigadiers',
        'data_base',
    ]

    def __init__(self, user):
        self.user = user
        self.data_path = (
            super().get_root_path() / 'data' / 'main_career_report')
        self.salary_path = super().get_root_path() / 'data' / 'salary_worker'
        self.drillers_path = super().get_root_path() / 'data' / 'drillers'
        self.brigadiers_path = super().get_root_path() / 'data' / 'brigadiers'
        self.shifts = ['Смена 1', 'Смена 2']
        self.salary_workers = super().load_data(
            data_path=self.salary_path,
            user=user,
            )
        self.drillers = super().load_data(
            data_path=self.drillers_path,
            user=user,
            )
        self.brigadiers = super().load_data(
            data_path=self.brigadiers_path,
            user=user,
            )
        self.data_base = super().load_data(
            data_path=self.data_path,
            user=user,
            )

    @classmethod
    def _create_workers_hours_list(
            cls,
            workers_list: List[str]
    ) -> Dict[str, int]:
        """Create workers hous list."""
        print("\nВведите количество часов:")
        workers_hours = {}
        for worker in workers_list:
            print(worker, end="")
            hours = input('; часов: ')
            workers_hours[worker] = int(hours)
        return workers_hours

    def _input_result(self, report: MainReportS) -> MainReportS:
        """Input working result"""
        for item in report.result:
            if isinstance(report.result[item], dict):
                for sub_item in report.result[item]:
                    print(sub_item, end='')
                    report.result[item][sub_item] = (super()
                                                     .float_input(msg=': '))
            elif item == 'шпурометры':
                drill_meters = self._give_drill_meters(report)
                print(item + f": {drill_meters} м.")
                add_meters = self._add_meters()
                if add_meters:
                    drill_meters += add_meters
                    print(item + f": {drill_meters} м.")
                report.result['шпурометры'] = drill_meters
            else:
                print(item, end='')
                report.result[item] = super().float_input(msg=': ')
        return report

    def _add_meters(self) -> float:
        """Add or sub meters."""
        add_meters = 0
        choise = input("[A] - добавить или отнять метры: ")
        if choise.lower() in ['a', 'а']:
            add_meters = super().float_input(msg='Введите метры: ')
        return add_meters

    def _give_drill_meters(self, report: MainReportS) -> float:
        """Find driller and give his meters."""
        shift = report.status['shift']
        drill_meters = DrillPassports(self.user).count_param_from_passports(
            driller=self.find_driller(shift),
            rep_date=report.status['date'],
            parametr='totall_meters',
        )
        return drill_meters

    def find_driller(self, shift: str) -> str:
        """Find Driller in shift."""
        for worker in self.drillers:
            if worker in AllWorkers(self.user).give_workers_from_shift(shift):
                driller = worker
                break
        return driller

    def _change_hours(self, tmp_rpt: MainReportS) -> MainReportS:
        """Change hours value."""
        print("Выберете работника для редактирования:")
        workers = tmp_rpt.workers_showing['факт']['часы']
        worker = super().choise_from_list(workers)
        new_hours = int(input("Введите новое значение часов: "))
        tmp_rpt.workers_showing['факт']['часы'][worker] = new_hours
        return tmp_rpt

    def _add_worker_from_diff_shift(self, shift: str):
        """Add worker from different shift to current."""
        added_workers = []
        self.shifts.remove(shift)
        different_shift = self.shifts[0]
        other_shift_workers = (
            AllWorkers(self.user).give_workers_from_shift(different_shift))
        while True:
            add_worker = input(
                "\nДобавить работника из другой бригады? Y/N: ")
            if add_worker.lower() == 'y':
                worker = super().choise_from_list(other_shift_workers)
                print(worker, '- добавлен.')
                added_workers.append(worker)
                other_shift_workers.remove(worker)
            elif add_worker.lower() == 'n':
                return added_workers
            else:
                print("Введите 'Y' или 'N'.")

    def _check_if_report_exist(self, shift: str, date: str):
        """Check if report exist in base"""
        check = True
        for report in self.data_base:
            if shift in report and date in report:
                check = False
                super().clear_screen()
                print("\033[91mТакой отчет уже существует.\033[0m")
        return check

    def _uncomplete_main_report(self, report_name: str):
        """Uncomlete main report"""
        choise = input("Are you shure, you want to uncomplete report? Y/n: ")
        if choise.lower() == 'y':
            tmp_rpt = self.data_base[report_name]
            tmp_rpt.status['status'] = '\033[93m[в процессе]\033[0m'
            new_name = "{date} {shift} {status}".format(
                **tmp_rpt.status)
            self.data_base[new_name] = tmp_rpt
            self.data_base.pop(report_name, self.user)
            super().dump_data(
                data_path=self.data_path,
                base_to_dump=self.data_base,
                user=self.user,
            )
            LOGGER.warning(
                f"User '{self.user.login}' uncomplete report: {new_name}"
            )

    def _delete_report(self, report_name: str):
        """Delete report."""
        if super().confirm_deletion(report_name):
            self.data_base.pop(report_name, None)
            super().dump_data(
                data_path=self.data_path,
                base_to_dump=self.data_base,
                user=self.user,
            )
            LOGGER.warning(
                f"User '{self.user.login}' delete report: {report_name}"
            )

    def _edit_salary_or_drillers(self, data_path: 'PurePath'):
        """Edit sallary or drillers lists."""
        while True:
            super().clear_screen()
            worker_list = super().load_data(
                data_path=data_path,
                user=self.user,
            )
            print("Работники в данной группе:")
            for worker in worker_list:
                print('\t', worker)
            edit_menu_dict = {'a': self._add_salary_or_driller,
                              'd': self._delete_salary_or_driller}
            action_name = input("Добавить или удалить работника (A/d): ")
            if action_name.lower() not in edit_menu_dict:
                print("Вы отменили редактирование.")
                break
            else:
                edit_menu_dict[action_name](data_path)

    def _add_salary_or_driller(self, data_path: 'PurePath'):
        """Add worker from salary or driller list."""
        worker_list = super().load_data(
            data_path=data_path,
            user=self.user,
        )
        if not worker_list:
            worker_list = []
        print("Выберете работника:")
        worker = super(Reports, self).choise_from_list(
            AllWorkers(self.user).give_mining_workers(), none_option=True
        )
        if worker:
            worker_list.append(worker)
            super().dump_data(
                data_path=data_path,
                base_to_dump=worker_list,
                user=self.user,
            )
            print("worker {} aded".format(worker))
            LOGGER.warning(
                f"User '{self.user.login}' add worker {worker} to list"
            )

    def _delete_salary_or_driller(self, data_path: 'PurePath'):
        """Delete worker from salary or driller list."""
        worker_list = super().load_data(
            data_path=data_path,
            user=self.user,
        )
        if not worker_list:
            worker_list = []
        print("Выберете работника для удаления:")
        worker = super(Reports, self).choise_from_list(
            worker_list, none_option=True)
        if worker:
            worker_list.remove(worker)
            super().dump_data(
                data_path=data_path,
                base_to_dump=worker_list,
                user=self.user,
            )
            print("worker {} deleted".format(worker))
            LOGGER.warning(
                f"User '{self.user.login}' delete worker {worker} from list"
            )

    def _edit_main_report(self, report_name: str):
        """
        Edition main report by boss or admin usser.
        """
        while True:
            tmp_rpt = self.data_base[report_name]
            print(tmp_rpt)
            if '[завершен]' in report_name:
                self._working_with_main_report(report_name)
                break
            edit_menu_dict = {
                'ввести горную массу': self._enter_rock_mass,
                'ввести итоговую сумму': self._enter_totall,
                'ежемесячный бонус': self._enter_bonus,
                'изменить КТУ работника': self._change_ktu,
                'удалить отчет': self._delete_report,
                'создать лист КТУ': DumpToExl().dump_ktu,
                '\033[92mсформировать отчет\033[0m':
                self._complete_main_report,
                '[закончить редактирование]': 'break'
                }
            print("Выберете пункт для редактирования:")
            action_name = super().choise_from_list(edit_menu_dict)
            print()
            if action_name in ['[закончить редактирование]', '']:
                break
            elif action_name == 'удалить отчет':
                tmp_rpt = edit_menu_dict[action_name](report_name)
                break
            elif action_name == 'создать лист КТУ':
                edit_menu_dict[action_name](tmp_rpt)
                continue
            tmp_rpt = edit_menu_dict[action_name](tmp_rpt)
            self.data_base.pop(report_name, None)
            report_name = "{date} {shift} {status}".format(
                **tmp_rpt.status)
            self.data_base[report_name] = tmp_rpt
            super().dump_data(
                data_path=self.data_path,
                base_to_dump=self.data_base,
                user=self.user,
            )
            super().clear_screen()

    def _enter_rock_mass(self, tmp_rpt: MainReportS) -> MainReportS:
        """Enter rock_mass"""
        print("Введите горную массу:")
        for gorizont in sorted(tmp_rpt.rock_mass):
            print(gorizont, end='')
            tmp_rpt.rock_mass[gorizont] = super().float_input(msg=': ')
        return tmp_rpt

    def _enter_totall(self, tmp_rpt: MainReportS) -> MainReportS:
        """Enter totall money"""
        tmp_rpt.totall = (super()
                          .float_input(msg="Введите итоговую сумму: "))
        return tmp_rpt

    @classmethod
    def _enter_bonus(cls, tmp_rpt: MainReportS) -> MainReportS:
        """Enter monthly bonus"""
        choise = input("Бригада победила в соревновании? Y/N: ")
        if choise.lower() == 'y':
            tmp_rpt.bonuses['победа по критериям'] = True
        return tmp_rpt

    def _change_ktu(self, tmp_rpt: MainReportS) -> MainReportS:
        """Manualy change worker KTU"""
        print("Выберете вид КТУ:")
        ktu_option = tmp_rpt.workers_showing
        direction = super().choise_from_list(ktu_option)
        print("Выберете работника:")
        workers = tmp_rpt.workers_showing[direction]['КТУ']
        ch_worker = super().choise_from_list(workers)
        new_ktu = super().float_input(msg="Введите новое значение КТУ: ")
        delta = (tmp_rpt.workers_showing[direction]['КТУ'][ch_worker]
                 - new_ktu)

        workers = super().count_unzero_items(
            tmp_rpt.workers_showing[direction]['КТУ'])
        tmp_rpt.workers_showing[direction]['КТУ'][ch_worker] = new_ktu
        for worker in tmp_rpt.workers_showing[direction]['КТУ']:
            unzero_worker = (
                tmp_rpt.workers_showing[direction]['КТУ'][worker] != 0)
            if worker != ch_worker and unzero_worker:
                tmp_rpt.workers_showing[direction]['КТУ'][worker] = round(
                    tmp_rpt.workers_showing[direction]['КТУ'][worker]
                    + round(delta/(workers-1), 2), 2)
        tmp_rpt.coutn_delta_ktu(direction)
        return tmp_rpt

    def _complete_main_report(self, tmp_rpt: MainReportS) -> MainReportS:
        """Complete main report"""
        choise = input("Вы уверены что хотите завершить отчет? Y/N: ")
        if choise.lower() == 'y':
            tmp_rpt.count_all_workers_in_report(self.user)
            tmp_rpt.status['status'] = '\033[92m[завершен]\033[0m'
            AllWorkers(self.user).add_salary_to_workers(
                tmp_rpt.workers_showing['факт']['зарплата'],
                tmp_rpt.status['date'],
                tmp_rpt.unofficial_workers()
            )
            LOGGER.warning(
                f"User '{self.user.login}' complete main report: "
                + f"{tmp_rpt.status['date']}"
            )
            backup_data = Thread(
                target=EmailSender(self.user).make_backup,
                args=(self.user,)
            )
            backup_data.start()
            LOGGER.warning(f"User '{self.user.login}' Make backup.")
        return tmp_rpt

    def _make_status_in_process(self, report_name: str):
        """Change status from 'not complete' to 'in process'"""
        print(self.data_base[report_name])
        tmp_report = self.data_base[report_name]
        print("Введите ОФИЦИАЛЬНЫЕ часы работы:")
        shift = tmp_report.status['shift']
        workers_list = AllWorkers(self.user).give_workers_from_shift(shift)
        workers_hours_list = self._create_workers_hours_list(workers_list)
        tmp_report.workers_showing['бух.']['часы'] = workers_hours_list
        super().clear_screen()
        tmp_report.create_ktu_list()
        tmp_report.count_all_workers_in_report(self.user)
        tmp_report.status['status'] = '\033[93m[в процессе]\033[0m'
        self.data_base.pop(report_name, None)
        new_name = "{date} {shift} {status}".format(**tmp_report.status)
        self.data_base[new_name] = tmp_report
        super().dump_data(
            data_path=self.data_path,
            base_to_dump=self.data_base,
            user=self.user,
        )
        LOGGER.warning(
            f"User '{self.user.login}' make report: "
            + f"{new_name}"
        )
        self._edit_main_report(new_name)

    def _print_workers_group(self):
        """Print additional workers group."""
        workers_group = {
            '[1] Окладники:': self.salary_workers,
            '[2] Бурильщики:': self.drillers,
            '[3] Бригадиры:': self.brigadiers
        }
        for workers_type in sorted(workers_group):
            print(workers_type)
            for worker in workers_group[workers_type]:
                print('\t', worker)

    def _choose_by_year(self) -> int:
        """Choose reports by year."""
        years = {
            report.split('-')[0]
            for report in self.data_base
        }
        print("[ENTER] - выйти."
              "\nВыберете год:")
        if not years:
            print("Наряды отсутствуют.")
        year = super().choise_from_list(years, none_option=True)
        if not year:
            raise MainMenu
        return year

    def _working_with_main_report(self, report_name):
        """Working with main report."""
        if '[не завершен]' in report_name:
            self._make_status_in_process(report_name)
        elif '[в процессе]' in report_name:
            self._edit_main_report(report_name)
        elif '[завершен]' in report_name:
            print(self.data_base[report_name])
            print("[E] - сохранить в данные в exel табель.")
            if self.user.accesse == 'admin':
                print(
                    "\033[91m[un]\033[0m Возвратить статус "
                    "'\033[93m[в процессе]\033[0m'\n"
                )
            choise = input()
            if choise.lower() in ['e', 'е']:
                DumpToExl().dump_salary(
                    report=self.data_base[report_name],
                    user=self.user,
                )
            elif self.user.accesse == 'admin' and choise == 'un':
                self._uncomplete_main_report(report_name)

    def choose_salary_or_drillers(self):
        """Chose list to edit, salary or drillers."""
        self._print_workers_group()
        choose = input("\n[ENTER] - выйти."
                       "\nВыберете тип работников для редактирования: ")
        if choose == '1':
            self._edit_salary_or_drillers(self.salary_path)
            LOGGER.warning(
                f"User '{self.user.login}' working with salary list")
        elif choose == '2':
            self._edit_salary_or_drillers(self.drillers_path)
            LOGGER.warning(
                f"User '{self.user.login}' working with drillers list")
        elif choose == '3':
            self._edit_salary_or_drillers(self.brigadiers_path)
            LOGGER.warning(
                f"User '{self.user.login}' working with brigadiers list")

    def give_main_results(self, year: str, month: str, shift: str):
        """Return drill meters, result and rock_mass.
        Return None, if report not exist."""
        report_name = year + '-' + month + ' ' + shift
        result_tuplet = ()
        for report in self.data_base:
            if (report_name in report and
                    self.data_base[report].count_result() != 0):
                drill_meters = self.data_base[report].result['шпурометры']
                result = self.data_base[report].count_result()
                rock_mass = self.data_base[report].count_rock_mass()
                result_tuplet = drill_meters, result, rock_mass
        return result_tuplet

    def give_avaliable_to_edit(self, *statuses) -> List[str]:
        """Give reports that avaliable to edit"""
        avaliable_reports = []
        avaliable_reports = [
            report
            for status in statuses
            for report in self.data_base
            if status in report
        ]
        return avaliable_reports

    def create_report(self):
        """Create New main report."""
        while True:
            rep_date = input("[ENTER] - выход"
                             "\nВведите дату отчета в формате 2018-12: ")
            if not rep_date:
                raise MainMenu
            if not super().check_date_format(rep_date):
                print("Введите дату корректно.")
                continue
            print("Выберете бригаду:")
            shift = super().choise_from_list(self.shifts)
            if self._check_if_report_exist(shift, rep_date):
                break

        workers_list = AllWorkers(self.user).give_workers_from_shift(shift)
        print(shift)
        for worker in workers_list:
            print(worker)

        # Add additional workers from another shift.
        added_workers = self._add_worker_from_diff_shift(shift)
        workers_list.extend(added_workers)
        super().clear_screen()

        report = MainReportS('\033[91m[не завершен]\033[0m', shift, rep_date)
        workers_hours_list = self._create_workers_hours_list(workers_list)
        report.workers_showing['факт']['часы'] = workers_hours_list
        print("\nВведите результаты добычи бригады.")
        report = self._input_result(report)
        print("\nТабель бригады заполнен.\n")
        report_name = "{date} {shift} {status}".format(**report.status)
        self.data_base[report_name] = report
        super().dump_data(
            data_path=self.data_path,
            base_to_dump=self.data_base,
            user=self.user,
        )
        LOGGER.warning(
            f"User '{self.user.login}' create main report: {report_name}")
        input('\n[ENTER] - выйти.')

    def edit_report(self):
        """
        Edition uncompleted report by user with 'master' accesse.
        """
        avaliable_reports = self.give_avaliable_to_edit('[не завершен]')
        print("""\
Вам доступны для редактирования только отчеты со статусом: \
\033[91m[не завершен]\033[0m
Выберет отчет для редактирования:
[ENTER] - выйти.
""")
        report_name = super().choise_from_list(
            avaliable_reports, none_option=True)
        if report_name:
            LOGGER.warning(
                f"User '{self.user.login}' edit main report: {report_name}")
        super().clear_screen()
        while report_name:
            tmp_rpt = self.data_base[report_name]
            print(tmp_rpt)
            edit_menu_dict = {
                'изменить часы': self._change_hours,
                'удалить отчет': self._delete_report,
                'изменить добычу': self._input_result,
                '[закончить редактирование]': 'break'
                }
            print("Выберете пункт для редактирования:")
            action_name = super().choise_from_list(edit_menu_dict)
            print()
            if action_name in ['[закончить редактирование]', '']:
                break
            elif action_name == 'удалить отчет':
                tmp_rpt = edit_menu_dict[action_name](report_name)
                break
            tmp_rpt = edit_menu_dict[action_name](tmp_rpt)
            self.data_base[report_name] = tmp_rpt
            super().dump_data(
                data_path=self.data_path,
                base_to_dump=self.data_base,
                user=self.user,
            )
            super().clear_screen()

    def choose_main_report(self):
        """Choose MainReport"""
        year = self._choose_by_year()
        while True:
            reports_by_year = [
                report
                for report in self.data_base
                if report.startswith(year)
            ]
            super().clear_screen()
            print("[ENTER] - выход."
                  "\nВыберет отчет:")
            report_name = super().choise_from_list(reports_by_year,
                                                   none_option=True)
            if not report_name:
                raise MainMenu
            self._working_with_main_report(report_name)
