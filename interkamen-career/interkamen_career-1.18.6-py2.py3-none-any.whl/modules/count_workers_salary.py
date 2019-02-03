#!/usr/bin/env python3
"""Count workers salary."""

from typing import Dict
import pandas as pd
from .workers_module import AllWorkers
from .workers_salary import WorkersSalary
from .administration.logger_cfg import Logs
from .support_modules.custom_exceptions import MainMenu
from .support_modules.dump_to_exl import DumpToExl


LOGGER = Logs().give_logger(__name__)


class SalaryCounter(AllWorkers):
    """Count workers salary."""

    __slots__ = (
        'temp_salary_file',
        'workers_salary_path',
        'workers_salary_file',
    )

    columns = [
        'year', 'month', 'shift', 'name', 'profession', 'days', 'salary'
    ]

    def __init__(self, user):
        """Load salary and workers data."""
        super().__init__(user)
        self.temp_salary_file = pd.DataFrame()
        self.workers_salary_path = (
            super().get_root_path() / 'data' / 'workers_salary'
        )
        if self.workers_salary_path.exists():
            self.workers_salary_file = super().load_data(
                data_path=self.workers_salary_path,
                user=user,
            )
        else:
            self.workers_salary_file = pd.DataFrame()

    @classmethod
    def _select_worker(cls, choise: str, dataframe: pd.DataFrame):
        """Select machine from data frame."""
        name = list(dataframe.name)[int(choise)]
        select_name = dataframe['name'] == name
        print('\n', '\033[92m', name, '\033[0m')
        return select_name

    def _dump_salary_data(self):
        """Dump salary data to file."""
        super().dump_data(
            data_path=self.workers_salary_path,
            base_to_dump=self.workers_salary_file,
            user=self.user,
        )

    def _save_workers_salary(self):
        """Save mech econom and create log file."""
        if self.workers_salary_file.empty:
            self.workers_salary_file = self.temp_salary_file
        else:
            self.workers_salary_file = self.workers_salary_file.append(
                self.temp_salary_file
            )
        self._dump_salary_data()

    def _give_workers_list(self, shift: str):
        """Made workers list."""
        career_workers = super().comp_structure['Карьер']
        if shift == 'Смена 1':
            workers_list = (
                career_workers['Инженерная служба']['Смена 1']
                + career_workers['Инженерная служба']['Смена 2']
                + career_workers['Механическая служба']['Смена 1']
                + career_workers['Другие работники']['Смена 1']
                + career_workers['Другие работники']['Регуляный']
            )
        elif shift == 'Смена 2':
            workers_list = (
                career_workers['Механическая служба']['Смена 2']
                + career_workers['Другие работники']['Смена 2']
            )
        return workers_list

    def _input_work_days(self, salary_date: Dict):
        """Input workers work days."""
        workers_list = self._give_workers_list(salary_date['shift'])
        salary_dict = {}
        print("Введите количество отработанных смен:")
        for worker in workers_list:
            salary_dict['year'] = salary_date['year']
            salary_dict['month'] = salary_date['month']
            salary_dict['shift'] = salary_date['shift']
            salary_dict['name'] = worker
            salary_dict['profession'] = self._give_profession(worker)
            salary_dict['days'] = int(input(f"{worker}: "))
            salary_dict['salary'] = self._count_salary(
                worker,
                salary_dict['profession'],
                salary_dict['days']
            )
            self.temp_salary_file = self.temp_salary_file.append(
                salary_dict, ignore_index=True
            )
        self.temp_salary_file = self.temp_salary_file[self.columns]
        self._check_and_save(salary_date)

    def _give_profession(self, worker: str):
        """Return worker profession."""
        w_profession = super().workers_base[worker].working_place['profession']
        return w_profession

    def _count_salary(self, worker, profession, days):
        """Count salary to worker."""
        w_salary = WorkersSalary(self.user).salary_list['Карьер'][profession]
        if worker in (
            super().comp_structure['Карьер']['Другие работники']['Регуляный']
        ):
            standart_days = 20
        else:
            standart_days = 15
        month_salary = round(w_salary / standart_days * days, 2)
        return month_salary

    def _save_report_and_make_log(self, salary_date: Dict):
        """Make log about report savre."""
        self._save_workers_salary()
        LOGGER.warning(
            f"User '{self.user.login}' create workers salary: "
            + '{year}.{month}-{shift}'.format(**salary_date)
        )
        print("\n\033[92mДанные сохранены.\033[0m")
        input('\n[ENTER] - выйти.')

    def _make_salary_dict(self) -> Dict:
        """Make salary dict from dataframe."""
        salary_dict = {
            name: salary
            for name, salary in zip(
                self.temp_salary_file.name,
                self.temp_salary_file.salary
            )
        }
        return salary_dict

    def _make_date(self, salary_date):
        """Make date to worker salary in worker profile."""
        if len(str(salary_date['month'])) == 1:
            salary_date['month'] = '0' + str(salary_date['month'])
        salary_date = '{year}-{month}'.format(**salary_date)
        return salary_date

    def _check_and_save(self, salary_date: Dict):
        """Check data and save to base."""
        while True:
            super().clear_screen()
            print('{}.{}-{}'.format(*map(str, salary_date.values())))
            print(self.temp_salary_file[
                ['name', 'profession', 'days', 'salary']
            ])
            choise = input(
                "\n[D] - выйти и \033[91mУДАЛИТЬ\033[m данные."
                "\n[S] - \033[92mСОХРАНИТЬ\033[0m отчет.\n"
                "\n[E] - экспортировать в exel файл."
                "\nВыберете работника для редактирования: "
            )
            if choise.lower() == 's':
                AllWorkers(self.user).add_salary_to_workers(
                    salary_dict=self._make_salary_dict(),
                    salary_date=self._make_date(salary_date)
                )
                self._save_report_and_make_log(salary_date)
                break
            elif choise.lower() == 'd':
                if super().confirm_deletion('отчет'):
                    break
                continue
            elif choise.lower() == 'e':
                DumpToExl.dump_worker_salary(self.temp_salary_file)
                continue
            elif not choise.isdigit():
                continue
            elif int(choise) > self.temp_salary_file.shape[0]:
                continue
            select_worker = self._select_worker(choise, self.temp_salary_file)
            self._add_another_days(select_worker)

    def _add_another_days(self, worker: pd.Series):
        """Add another days to worker."""
        self.temp_salary_file.loc[worker, 'days'] = int(input("дней: "))
        self.temp_salary_file.loc[worker, 'salary'] = self._count_salary(
            self.temp_salary_file[worker].name.values[0],
            self.temp_salary_file[worker].profession.values[0],
            int(self.temp_salary_file[worker].days)
        )

    def _make_report_temp(self, rep_date: Dict):
        """Make report of day temr and drop it from DF."""
        self.temp_salary_file = self.workers_salary_file[
            (self.workers_salary_file['year'] == rep_date['year'])
            & (self.workers_salary_file['month'] == rep_date['month'])
            & (self.workers_salary_file['shift'] == rep_date['shift'])
        ]
        self.workers_salary_file = self.workers_salary_file.append(
            self.temp_salary_file).drop_duplicates(keep=False)
        self._dump_salary_data()

    def count_salary_workers(self):
        """Count salary to non_brigade workers."""
        while True:
            salary_date = super().input_date()
            if not salary_date:
                break
            print("Выберете смену:")
            shift = super().choise_from_list(['Смена 1', 'Смена 2'])
            if not shift:
                raise MainMenu
            salary_date.update({'shift': shift})
            check = super().check_date_in_dataframe(
                self.workers_salary_file,
                salary_date
            )
            if check:
                print("Данные за этот месяц уже внесены.")
                input("\n[ENTER] - выйти.")
            else:
                self._input_work_days(salary_date)
                break

    def edit_report(self):
        """Show report for current month."""
        print("[ENTER] - выйти."
              "\nВыберете год:")
        year = super().choise_from_list(
            sorted(set(self.workers_salary_file.year)),
            none_option=True
        )
        if not year:
            raise MainMenu
        print("Выберете месяц:")
        data_by_year = self.workers_salary_file[
            self.workers_salary_file.year == year
        ]
        month = super().choise_from_list(sorted(set(data_by_year.month)))
        shifts = set(sorted(
            data_by_year[data_by_year.month == month]['shift']
        ))
        print("Выберете смену:")
        shift = super().choise_from_list(shifts)
        if shift:
            rep_date = {
                'year': int(year),
                'month': int(month),
                'shift': shift,
            }
            self._make_report_temp(rep_date)
            self._check_and_save(rep_date)
