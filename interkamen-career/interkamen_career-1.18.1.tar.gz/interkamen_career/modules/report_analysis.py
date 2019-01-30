#!/usr/bin/env python3
"""
Module that provide to analyse and visualise MainReport data.

.result_analysis() - create plots for analyse brigade results.

.rock_mass_analysis() - create plots for analyse brigade rock mass.
"""

from typing import Dict, List
from collections import namedtuple
from copy import deepcopy
from matplotlib import pyplot as plt
from .main_career_report import Reports
from .support_modules.custom_exceptions import MainMenu


class ReportAnalysis(Reports):
    """Class to anilise and visualisate data from Main reports."""

    __slots__ = [
        'base',
        'shifts',
    ]

    Statistic = namedtuple('Statistic', ['result', 'title1', 'title2'])
    HorizontResults = namedtuple('HorizontResults', [
        'horizont_sum',
        'monthly_sum',
        'rock_mass_month',
        'rock_mass_horizont',
    ])
    ShiftResults = namedtuple('ShiftResults', [
        'shift_sum',
        'rock_mass_shift'
    ])
    horizonts = ['+108', '+114', '+120', '+126', '+132']
    month_list = ['01', '02', '03', '04', '05', '06',
                  '07', '08', '09', '10', '11', '12']

    by_horizont = {
        'res': {
            '+108': [],
            '+114': [],
            '+120': [],
            '+126': [],
            '+132': [],
            'totall': [],
        },
        'pers': {
            '+108': [],
            '+114': [],
            '+120': [],
            '+126': [],
            '+132': [],
            'totall': [],
        },
        'rock_mass': {
            '+108': [],
            '+114': [],
            '+120': [],
            '+126': [],
            '+132': [],
            'totall': [],
        }
    }
    by_shift = {
        'res': {
            'Смена 1': [],
            'Смена 2': [],
            },
        'pers': {
            'Смена 1': [],
            'Смена 2': [],
            },
        'rock_mass': {
            'Смена 1': [],
            'Смена 2': [],
            }
    }
    year_reports = {}

    def __init__(self, user):
        """Prepare data."""
        super().__init__(user)
        self.shifts = ['Смена 1', 'Смена 2']
        self.base = super().load_data(
            data_path=self.data_path,
            user=self.user,
        )

    @classmethod
    def count_pers(cls, rock_mass: float, result: float):
        """Count persent."""
        if rock_mass != 0:
            persent = round(result/rock_mass*100, 2)
        else:
            persent = 0
        return persent

    def _chose_year(self):
        """Chose avaliable year."""
        avaliable_years = {
            report.split(' ')[0].split('-')[0]
            for report in self.base
        }
        return avaliable_years

    def _give_reports_by_year(self, year):
        """Give reports of current year from reports base."""
        for report in self.base:
            if year in report:
                self.year_reports[report] = self.base[report]

    def _data_print(self, year, data_dict: Dict[str, int]):
        """Pretty data print.

        data_dict is dictionary with keys: percent, result, rock_mass.
        """
        output = "\033[92m" + year + ' год\n' + "\033[0m"
        output += "{:^100}\n".format('месяц')
        output += "           {}\n".format('     '.join(self.month_list))
        output += '-' * 94 + '\n'
        for item in data_dict:
            for sub_item in sorted(data_dict[item]):
                output += """\
{:<7}: |{:^6}|{:^6}|{:^6}|{:^6}|{:^6}|\
{:^6}|{:^6}|{:^6}|{:^6}|{:^6}|{:^6}|{:^6}|\

""".format(sub_item, *data_dict[item][sub_item])
        print(output)

    def _make_brigade_financial_statistic(self, sal_anal):
        """Make brigade salary and brigade results statistic by month."""
        result = {
            'indicators': {
                'res': [],
                'rock_mass': [],
                'salary': [],
            },
            'cost': {
                'cost': []
            }
        }
        shift_results = self._give_by_shift()
        shift_results.pop('pers', None)
        result['indicators'] = {
            direction: list(map(sum, zip(
                shift_results[direction]['Смена 1'],
                shift_results[direction]['Смена 2']
            )))
            for direction in shift_results
        }
        result['indicators']['rock_mass'] = [
            int(round(rock_mass/10, 2))
            for rock_mass in result['indicators']['rock_mass']
        ]
        brig_salary = self._give_totall_fact_salary()
        result['indicators']['salary'] = [
            round(salary/1000, 0)
            for salary in brig_salary
        ]
        result['cost']['cost'] = [
            int(round(salary/result, 0))
            for salary, result in zip(
                brig_salary,
                result['indicators']['res']
            )
            if result != 0
        ]
        if sal_anal:
            result = self._create_analise_data(result, sal_anal)
        title1 = 'Стоимость одного м\u00B3 продукции, р'
        title2 = (
            'Зарплата бригады, тыс.р; '
            'Горная масса, м\u00B3*10; '
            'Кубатура, м\u00B3'
        )
        stat = self.Statistic(result, title1, title2)
        return stat

    @classmethod
    def _create_analise_data(cls, result, sal_anal):
        """Create data to analise."""
        cost_min_up_cube = sal_anal.up_salary / sal_anal.up_shift
        down_shift = sal_anal.min_salary / cost_min_up_cube
        progect_salary_list = []
        for res in result['indicators']['res']:
            # Count KTU workers.
            if res < down_shift*2:
                ktu_sal = sal_anal.min_salary
            else:
                ktu_sal = res * cost_min_up_cube / 2

            month_salary = ktu_sal*18 + sal_anal.bonus*9

            progect_salary_list.append(month_salary)

        result['indicators']['progect_salary'] = [
            int(round(progect_salary/1000, 0))
            for progect_salary in progect_salary_list
        ]
        result['cost']['progect_cost'] = [
            int(round(progect_salary/res, 0))
            for progect_salary, res in zip(
                progect_salary_list,
                result['indicators']['res']
            )
        ]
        return result

    def _make_rock_mass_statistic(self):
        """Make horisont and shift statistic by month."""
        result = {}
        result['shift'] = self._give_by_shift()['rock_mass']
        result['horiz'] = self._give_by_horiz()['rock_mass']
        stat = self.Statistic(
            result,
            'Горная масса по горизонтам, м\u00B3',
            'Горная масса по вахтам, м\u00B3'
        )
        return stat

    def _make_shift_statistic(self):
        """Make result and persent statistic by shift."""
        result = self._give_by_shift()
        # result == self.by_shift
        result.pop('rock_mass', None)
        stat = self.Statistic(
            result,
            'Повахтовый выход, %',
            'Повахтовая добыча м\u00B3'
        )
        return stat

    def _make_horizont_statistic(self):
        """Make result and persent statistic by horizont."""
        result = self._give_by_horiz()
        # result == self.by_horisond
        result.pop('rock_mass', None)
        stat = self.Statistic(
            result,
            'Погоризонтный выход, %',
            'Погоризонтная добыча, м\u00B3'
        )
        return stat

    @Reports.set_plotter_parametrs
    def _two_plots_show(self, year, stat, title):
        """Combine two subplots."""
        figure = plt.figure()
        suptitle = figure.suptitle(title, fontsize="x-large")

        plot_number = 1
        for result in sorted(stat.result):
            self._subplot_result(
                (figure, 120+plot_number),
                year,
                stat.result[result],
                stat[plot_number]
            )
            plot_number += 1

        figure.tight_layout()
        suptitle.set_y(0.95)
        figure.subplots_adjust(top=0.85)
        plt.show()

    @classmethod
    def _find_coeff_for_title_hight(cls, title):
        """Find title hight.

        Count coefficient for annotations coordinate depend on scale.
        """
        if title.split(' ')[1] in ['добыча,', 'масса']:
            coef = 5
        else:
            coef = 0.1
        return coef

    def _add_markers_to_plot(self, axle, item, title):
        """Add markers to plot."""
        coef = self._find_coeff_for_title_hight(title)
        for point in zip(self.month_list, item):
            if point[1] != 0:
                ann_text = str(point[1])
                ann_coord = (point[0], point[1]+coef)
                axle.annotate(ann_text, xy=ann_coord, fontsize='small')

    def _subplot_result(self, fig_plot, year, result, title):
        """Visualise result."""
        axle = fig_plot[0].add_subplot(fig_plot[1])
        for item in result:
            axle.plot(self.month_list, result[item], marker='D', markersize=4)
            self._add_markers_to_plot(axle, result[item], title)

        legend = self._replace_legend(result)
        axle.legend(legend)
        axle.set_xlabel('месяц')
        axle.set_ylabel(title.split(' ')[-1])
        axle.set_title(year + 'г., ' + title)
        axle.grid(b=True, linestyle='--', linewidth=0.5)

    def _replace_legend(self, result):
        """Replays legend to years totall."""
        legend = list(result.keys())
        for position, item in enumerate(legend):
            if item in ['salary', 'progect_salary']:
                year_sum = int(round(sum(result[item]), 0))
                legend[position] = f'{item} (year sum = {year_sum} Krub)'
        return legend

    def _count_horizont_results(self, report, month, horizont):
        """Give data from reports of current month."""
        report_month = report.split(' ')[0].split('-')[1]
        if report_month == month:
            month_res = self.HorizontResults(
                self.base[report].result['погоризонтно'][horizont],
                self.base[report].count_result(),
                self.base[report].count_rock_mass(),
                self.base[report].rock_mass[horizont]
            )
            return month_res

    def _count_shifts_results(self, report, month, shift):
        """Give data from reports of current month."""
        report_month = report.split(' ')[0].split('-')[1]
        report_shift = self.base[report].status['shift']
        if shift == report_shift and report_month == month:
            month_res = self.ShiftResults(
                self.base[report].count_result(),
                self.base[report].count_rock_mass()
            )
            return month_res

    def _fill_result_list(
            self,
            result_lists: Dict[str, Dict],
            *,
            rock_mass: float,
            res: float,
            data_by: str
    ) -> Dict[str, Dict]:
        """Fill result lists."""
        result_lists['pers'][data_by].append(self.count_pers(rock_mass, res))
        result_lists['rock_mass'][data_by].append(int(round(rock_mass, 0)))
        result_lists['res'][data_by].append(int(round(res, 0)))
        return result_lists

    def _give_by_horiz(self) -> Dict[str, Dict]:
        """Give result and persent horizont."""
        result_lists = deepcopy(self.by_horizont)
        for month in self.month_list:
            for horizont in self.horizonts:
                all_months_res = [
                    self._count_horizont_results(report, month, horizont)
                    for report in self.year_reports
                    if self._count_horizont_results(report, month, horizont)
                ]
                all_month = self.HorizontResults(*map(
                    sum,
                    zip(*all_months_res)
                ))
                result_lists = self._fill_result_list(
                    result_lists,
                    rock_mass=all_month.rock_mass_horizont,
                    res=all_month.horizont_sum,
                    data_by=horizont
                )
            result_lists = self._fill_result_list(
                result_lists,
                rock_mass=all_month.rock_mass_month,
                res=all_month.monthly_sum,
                data_by='totall'
                )
        return result_lists

    def _give_by_shift(self) -> Dict[str, int]:
        """Give result and persent by shift."""
        result_lists = deepcopy(self.by_shift)
        for month in self.month_list:
            for shift in self.shifts:
                for report in self.year_reports:
                    results = self._count_shifts_results(report, month, shift)
                    if results:
                        all_month = results
                        break
                result_lists = self._fill_result_list(
                    result_lists,
                    rock_mass=all_month.rock_mass_shift,
                    res=all_month.shift_sum,
                    data_by=shift
                )
        return result_lists

    def _give_totall_fact_salary(self) -> List[float]:
        """Give totall brigade salary by month."""
        salary_list = []
        for month in self.month_list:
            brigade_salary = [
                sum(
                    self.base[report].workers_showing['факт']['зарплата']
                    .values()
                )
                for report in self.year_reports
                if report.split(' ')[0].split('-')[1] == month
            ]
            salary_list.append(int(round(sum(brigade_salary), 0)))
        return salary_list

    def _choose_report_by_year(self):
        """Choose report by year from database."""
        print(
            "[ENTER] - выход"
            "\nВыберете год:"
        )
        year = super().choise_from_list(
            self._chose_year(),
            none_option=True,
        )
        if not year:
            raise MainMenu
        self._give_reports_by_year(year)
        super().clear_screen()
        return year

    def result_analysis(self):
        """Analysis by result."""
        year = self._choose_report_by_year()
        while True:
            data_type = {
                'Погоризонтная статистика': self._make_horizont_statistic,
                'Повахтовая статистика': self._make_shift_statistic,
            }
            print(
                "\n[ENTER] - выход"
                "\nВыберете необходимый очет: "
            )
            choise = super().choise_from_list(data_type, none_option=True)
            super().clear_screen()

            if choise in data_type:
                stat = data_type[choise]()
                self._data_print(year, stat.result)
                self._two_plots_show(year, stat, title="Результаты работы.")
            elif not choise:
                break
            else:
                print("Нет такого варианта.")
                continue

    def rock_mass_analysis(self):
        """Analysis by rock mass."""
        year = self._choose_report_by_year()
        rock_stat = self._make_rock_mass_statistic()
        self._data_print(year, rock_stat.result)
        self._two_plots_show(year, rock_stat, title="Результаты работы.")
        input('\n[ENTER] - выйти.')

    def brigade_financial_analysis(self):
        """Analysis brigade salary by brigade results."""
        year = self._choose_report_by_year()
        while True:
            sal_anal = self._add_analyse_option()
            fin_stat = self._make_brigade_financial_statistic(sal_anal)
            self._two_plots_show(
                year,
                fin_stat,
                title="Финансовые показатели."
            )

    @classmethod
    def _add_analyse_option(cls):
        """Add analyse to brigade salary."""
        choose = input(
            "\n[a] - Добавить анализ."
            "\n[s] - Только статистика."
            "\n[ENTER] - выйти в меню: "
        )
        if not choose:
            raise MainMenu
        elif choose.lower() == 'a':
            analyse = namedtuple('Analyse', [
                'up_shift',
                'min_salary',
                'up_salary',
                'bonus'
            ])
            sal_anal = analyse(
                int(input("Введите верхнюю границу: ")),
                int(input("Введите минимальный оклад: ")),
                int(input("Введите з/п верхней границы: ")),
                int(input("Введите приработок 'специалистов': ")),
            )
        else:
            sal_anal = None
        return sal_anal
