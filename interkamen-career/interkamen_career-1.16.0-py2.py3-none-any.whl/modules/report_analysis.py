#!/usr/bin/env python3
"""
Module that provide to analyse and visualise MainReport data.

.result_analysis() - create plots for analyse brigade results.

.rock_mass_analysis() - create plots for analyse brigade rock mass.
"""

from collections import namedtuple
from copy import deepcopy
from matplotlib import pyplot as plt
from .main_career_report import Reports
from .support_modules.custom_exceptions import MainMenu


class ReportAnalysis(Reports):
    """
    Class to anilise and visualisate data from reports.
    """

    __slots__ = [
        'base',
        'shifts',
    ]

    statistic = namedtuple('Statistic', ['result', 'title1', 'title2'])
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
            'totall': []
        },
        'pers': {
            '+108': [],
            '+114': [],
            '+120': [],
            '+126': [],
            '+132': [],
            'totall': []
        },
        'rock_mass': {
            '+108': [],
            '+114': [],
            '+120': [],
            '+126': [],
            '+132': [],
            'totall': []
        }
    }
    by_shift = {
        'res': {
            'Смена 1': [],
            'Смена 2': []
            },
        'pers': {
            'Смена 1': [],
            'Смена 2': []
            },
        'rock_mass': {
            'Смена 1': [],
            'Смена 2': []
            }
    }
    year_reports = {}

    def __init__(self, user):
        super().__init__(user)
        self.shifts = ['Смена 1', 'Смена 2']
        self.base = super().load_data(
            data_path=self.data_path,
            user=self.user,
        )

    @classmethod
    def count_persent(cls, rock_mass, result):
        """Count persent"""
        if rock_mass != 0:
            persent = round(result/rock_mass*100, 2)
        else:
            persent = 0
        return persent

    def _chose_year(self):
        """Chose avaliable year."""
        avaliable_years = {report.split(' ')[0].split('-')[0]
                           for report in self.base}
        return avaliable_years

    def _give_reports_by_year(self, year):
        """Give reports of current year from reports base"""
        for report in self.base:
            if year in report:
                self.year_reports[report] = self.base[report]

    def _data_print(self, year, data_dict):
        """
        Pretty data print.
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

    def _make_rock_mass_statistic(self):
        """Make horisont and shift statistic by month."""
        result = {}
        result['shift'] = self._give_by_shift()['rock_mass']
        result['horiz'] = self._give_by_horiz()['rock_mass']
        title1 = 'Горная масса по горизонтам, м\u00B3'
        title2 = 'Горная масса по вахтам, м\u00B3'
        stat = self.statistic(result, title1, title2)
        return stat

    def _make_shift_statistic(self):
        """Make result and persent statistic by shift."""
        result = self._give_by_shift()
        # result == self.by_shift
        result.pop('rock_mass', None)
        title1 = 'Повахтовый выход, %'
        title2 = 'Повахтовая добыча м\u00B3'
        stat = self.statistic(result, title1, title2)
        return stat

    def _make_horizont_statistic(self):
        """Make result and persent statistic by horizont."""
        result = self._give_by_horiz()
        # result == self.by_horisond
        result.pop('rock_mass', None)
        title1 = 'Погоризонтный выход, %'
        title2 = 'Погоризонтная добыча, м\u00B3'
        stat = self.statistic(result, title1, title2)
        return stat

    @Reports.set_plotter_parametrs
    def _two_plots_show(self, year, stat):
        """Combine two subplots"""
        figure = plt.figure()
        suptitle = figure.suptitle("Результаты работы.", fontsize="x-large")

        plot_number = 1
        for result in sorted(stat.result):
            self._subplot_result((figure, 120+plot_number),
                                 year,
                                 stat.result[result],
                                 stat[plot_number])
            plot_number += 1

        figure.tight_layout()
        suptitle.set_y(0.95)
        figure.subplots_adjust(top=0.85)
        plt.show()

    def _subplot_result(self, fig_plot, year, result, title):
        """visualise result."""
        # Count coefficient for annotations coordinate depend on scale.
        if title.split(' ')[1] in ['добыча,', 'масса']:
            coef = 5
        else:
            coef = 0.1

        axle = fig_plot[0].add_subplot(fig_plot[1])

        for item in sorted(result):
            axle.plot(self.month_list, result[item],
                      marker='D', markersize=4)
            for point in zip(self.month_list, result[item]):
                if point[1] != 0:
                    ann_text = str(point[1])
                    ann_coord = (point[0], point[1]+coef)
                    axle.annotate(ann_text, xy=ann_coord, fontsize='small')

        axle.legend(list(sorted(result.keys())))
        axle.set_xlabel('месяц')
        axle.set_ylabel(title.split(' ')[-1])
        axle.set_title(year + 'г., ' + title)
        axle.grid(b=True, linestyle='--', linewidth=0.5)

    def _give_by_horiz(self):
        """Give result and persent horizont"""
        result_lists = deepcopy(self.by_horizont)
        for month in self.month_list:
            for horizont in self.horizonts:
                horizont_sum = 0
                monthly_sum = 0
                rock_mass_month = 0
                rock_mass_horizont = 0
                for report in self.year_reports:
                    if report.split(' ')[0].split('-')[1] == month:
                        horizont_sum += (
                            self.base[report].result['погоризонтно'][horizont])
                        rock_mass_horizont += (
                            self.base[report].rock_mass[horizont])
                        monthly_sum += self.base[report].count_result()
                        rock_mass_month += self.base[report].count_rock_mass()
                persent = self.count_persent(rock_mass_horizont, horizont_sum)
                result_lists['pers'][horizont].append(persent)
                result_lists['rock_mass'][horizont].append(
                    int(round(rock_mass_horizont, 0)))
                result_lists['res'][horizont].append(
                    int(round(horizont_sum, 0)))
            persent = self.count_persent(rock_mass_month, monthly_sum)
            result_lists['pers']['totall'].append(persent)
            result_lists['res']['totall'].append(int(round(monthly_sum, 0)))
            result_lists['rock_mass']['totall'].append(
                int(round(rock_mass_month, 0)))
        return result_lists

    def _give_by_shift(self):
        """Give result and persent by shift."""
        result_lists = deepcopy(self.by_shift)
        for month in self.month_list:
            for shift in self.shifts:
                shift_sum = 0
                rock_mass_shift = 0
                for report in self.year_reports:
                    report_month = report.split(' ')[0].split('-')[1]
                    report_shift = self.base[report].status['shift']
                    if shift == report_shift and report_month == month:
                        shift_sum += self.base[report].count_result()
                        rock_mass_shift += self.base[report].count_rock_mass()
                persent = self.count_persent(rock_mass_shift, shift_sum)
                result_lists['pers'][shift].append(persent)
                result_lists['res'][shift].append(int(round(shift_sum, 0)))
                result_lists['rock_mass'][shift].append(
                    int(round(rock_mass_shift, 0)))
        return result_lists

    def result_analysis(self):
        """Analysis by result"""
        print("[ENTER] - выход"
              "\nВыберете год:")
        year = super().choise_from_list(
            self._chose_year(),
            none_option=True,
        )
        if not year:
            raise MainMenu
        self._give_reports_by_year(year)
        super().clear_screen()
        while True:
            data_type = {
                'Погоризонтная статистика': self._make_horizont_statistic,
                'Повахтовая статистика': self._make_shift_statistic
                }
            print("\n[ENTER] - выход"
                  "\nВыберете необходимый очет: ")
            choise = super().choise_from_list(data_type, none_option=True)
            super().clear_screen()

            if choise in data_type:
                stat = data_type[choise]()

                self._data_print(year, stat.result)
                self._two_plots_show(year, stat)

            elif not choise:
                break
            else:
                print("Нет такого варианта.")
                continue

    def rock_mass_analysis(self):
        """Analysis by rock mass."""
        print("[ENTER] - выход"
              "\nВыберете год:")
        year = super().choise_from_list(
            self._chose_year(),
            none_option=True,
        )
        if not year:
            raise MainMenu
        self._give_reports_by_year(year)
        super().clear_screen()
        rock_stat = self._make_rock_mass_statistic()
        self._data_print(year, rock_stat.result)
        self._two_plots_show(year, rock_stat)
        input('\n[ENTER] - выйти.')
