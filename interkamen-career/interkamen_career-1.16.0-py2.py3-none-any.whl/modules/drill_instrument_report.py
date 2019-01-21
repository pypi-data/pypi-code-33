#!/usr/bin/env python3
"""
Working with statistic of drill instrument.

.create_drill_report() - create new drill report.

.show_statistic_by_year() - show stats for drill instrumens by year.
"""

import os
from matplotlib import pyplot as plt
import pandas as pd
from .main_career_report import Reports
from .administration.logger_cfg import Logs
from .support_modules.custom_exceptions import MainMenu
from .drill_passports import DrillPassports
from .support_modules.standart_functions import (
    BasicFunctionsS
    as BasF_S
)

LOGGER = Logs().give_logger(__name__)


class DrillInstruments(BasF_S):
    """
    All information about drill instruments.
    """

    __slots__ = [
        'drill_path',
        'temp_drill_path',
        'user',
        'drill_file',
        'drill_data'
    ]

    month_list = ['01', '02', '03', '04', '05', '06',
                  '07', '08', '09', '10', '11', '12']

    def __init__(self, user):
        self.drill_data = {}
        self.drill_path = (
            super().get_root_path() / 'data' / 'drill_instruments')
        self.temp_drill_path = (
            super().get_root_path() / 'data' / 'temp_drill_inst')
        self.user = user
        if self.drill_path.exists():
            self.drill_file = super().load_data(
                data_path=self.drill_path,
                user=user,
            )
        else:
            self.drill_file = pd.DataFrame(self.drill_data, index=[0])
            super().dump_data(
                data_path=self.drill_path,
                base_to_dump=self.drill_file,
                user=user,
            )
        # Try to complete drill report if temp file exist.
        self._comlete_drill_report()

    @classmethod
    def _create_meters_by_month(cls, figure, data_by_year, shifts):
        """Totall drill meters in month by each shift."""
        met_bu_mon = figure.add_subplot(221)
        met_bu_mon.plot(data_by_year[shifts[0]].month,
                        data_by_year[shifts[0]].meters,
                        marker='D', markersize=4)
        met_bu_mon.plot(data_by_year[shifts[1]].month,
                        data_by_year[shifts[1]].meters,
                        marker='D', markersize=4)
        met_bu_mon.legend(['Смена 1', 'Смена 2'])
        met_bu_mon.set_ylabel('шпурометры, м.')
        met_bu_mon.grid(b=True, linestyle='--', linewidth=0.5)
        met_bu_mon.set_title('Пробурено за смену.')

    @classmethod
    def _create_all_bits(cls, figure, data_by_year, shifts, bits):
        """Totall used bits by shift and bits in rock."""
        all_bits = figure.add_subplot(222)
        all_bits.plot(data_by_year[shifts[0]].month, bits[0],
                      marker='D', markersize=4)
        all_bits.plot(data_by_year[shifts[1]].month, bits[1],
                      marker='D', markersize=4)
        all_bits.plot(data_by_year[shifts[0]].month,
                      data_by_year[shifts[0]].bits_in_rock,
                      marker='D', markersize=4)
        all_bits.plot(data_by_year[shifts[1]].month,
                      data_by_year[shifts[1]].bits_in_rock,
                      marker='D', markersize=4)
        all_bits.legend(['коронки, см.1', 'коронки, см.2',
                         'коронки в скале, см.1', 'коронки в скале, см.2'])
        all_bits.set_ylabel('количество, шт')
        all_bits.grid(b=True, linestyle='--', linewidth=0.5)
        all_bits.set_title('Истрачено коронок.')

    @classmethod
    def _create_meters_by_bits(cls, figure, data_by_year, shifts, bits):
        """Meters passed by one average bit."""
        met_by_bit = figure.add_subplot(223)
        meters_by_bits1 = data_by_year[shifts[0]].meters / bits[0]
        meters_by_bits2 = data_by_year[shifts[1]].meters / bits[1]
        met_by_bit.plot(data_by_year[shifts[0]].month, meters_by_bits1,
                        marker='D', markersize=4)
        met_by_bit.plot(data_by_year[shifts[1]].month, meters_by_bits2,
                        marker='D', markersize=4)
        met_by_bit.legend(['Смена 1', 'Смена 2'])
        met_by_bit.set_ylabel('метров / коронку')
        met_by_bit.set_xlabel('месяцы')
        met_by_bit.grid(b=True, linestyle='--', linewidth=0.5)
        met_by_bit.set_title('Проход одной коронки.')

    @classmethod
    def _create_bits_by_thousand_rocks(cls, figure, data_by_year,
                                       shifts, bits):
        """Bits by thousand rock mass."""
        bit_by_rock = figure.add_subplot(224)
        bits_by_thousand_rocks1 = (
            bits[0] / (data_by_year[shifts[0]].rock_mass / 1000)
            )
        bits_by_thousand_rocks2 = (
            bits[1] / (data_by_year[shifts[1]].rock_mass / 1000)
            )
        bit_by_rock.plot(data_by_year[shifts[0]].month,
                         bits_by_thousand_rocks1,
                         marker='D', markersize=4)
        bit_by_rock.plot(data_by_year[shifts[1]].month,
                         bits_by_thousand_rocks2,
                         marker='D', markersize=4)
        bit_by_rock.legend(['Смена 1', 'Смена 2'])
        bit_by_rock.set_ylabel('коронок / 1000м\u00B3 горной массы')
        bit_by_rock.set_xlabel('месяцы')
        bit_by_rock.grid(b=True, linestyle='--', linewidth=0.5)
        bit_by_rock.set_title('Коронок на тысячу кубов горной массы.')

    @classmethod
    def _print_statistic_by_year(cls, data):
        """Showing all drill data"""
        with pd.option_context('display.max_rows', None,
                               'display.max_columns', None):
            print(data)

    def _check_correctly_input(self, results_exist):
        """Check if data input corretly."""
        print("Отчет: ")
        for item in sorted(self.drill_data):
            print(item, ':', self.drill_data[item])
        confirm = input("\nПроверьте корректность ввода данных,\
если данные введены верно введите 'Y': ")
        if confirm.lower() == 'y' and results_exist:
            self._save_drill_report()
            print("Отчет по инструменту создан.")
        elif confirm.lower() == 'y' and not results_exist:
            self._save_drill_report_to_temp()
            print("Отчет по инструменту создан.")
        else:
            print("Вы отменили сохранение.")
        input("\n[ENTER] - выйти.")

    def _save_drill_report(self):
        """Save drill report and create log file."""
        self.drill_file = self.drill_file.append(self.drill_data,
                                                 ignore_index=True)
        super().dump_data(
            data_path=self.drill_path,
            base_to_dump=self.drill_file,
            user=self.user,
        )
        report_name = '{}-{}-{}'.format(self.drill_data['year'],
                                        self.drill_data['month'],
                                        self.drill_data['shift'])
        LOGGER.warning(
            f"User '{self.user.login}' create drill inst.: {report_name}"
        )

    def _visualise_statistic(self, year):
        """Visualise statistic."""
        drill_year = self.drill_file.year == year
        data_by_year = self.drill_file[drill_year].sort_values(by=['month'])
        self._print_statistic_by_year(data_by_year)
        shift1 = data_by_year['shift'] == 'Смена 1'
        shift2 = data_by_year['shift'] == 'Смена 2'
        all_bits1 = (data_by_year[shift1].bits32
                     + data_by_year[shift1].bits35)
        all_bits2 = (data_by_year[shift2].bits32
                     + data_by_year[shift2].bits35)
        self._create_plots(
            data_by_year,
            (shift1, shift2),
            (all_bits1, all_bits2)
            )

    @BasF_S.set_plotter_parametrs
    def _create_plots(self, data_by_year, shifts, bits):
        """Create plots for drill data."""

        figure = plt.figure()
        suptitle = figure.suptitle("Отчет по буровому инструменту.",
                                   fontsize="x-large")
        data_to_plot = (figure, data_by_year, shifts, bits)
        self._create_meters_by_month(*data_to_plot[:-1])
        self._create_all_bits(*data_to_plot)
        self._create_meters_by_bits(*data_to_plot)
        self._create_bits_by_thousand_rocks(*data_to_plot)

        figure.tight_layout()
        suptitle.set_y(0.95)
        figure.subplots_adjust(top=0.85)
        plt.show()

    def _input_other_stats(self):
        """Input other stats about drill instrument."""
        self.drill_data['bits32'] = int(input("коронки 32: "))
        self.drill_data['bits35'] = int(input("коронки 35: "))
        self.drill_data['bar3'] = int(input("штанги 3м: "))
        self.drill_data['bar6'] = int(input("штанги 6м: "))
        self.drill_data['driller'] = Reports(self.user).find_driller(
            self.drill_data['shift'])
        rep_date = f"{self.drill_data['year']}-{self.drill_data['month']}"
        self.drill_data['bits_in_rock'] = int(
            DrillPassports(self.user).count_param_from_passports(
                driller=self.drill_data['driller'],
                rep_date=rep_date,
                parametr='bits_in_rock',
            )
        )

    def _input_year_month_shift(self):
        """Check if main report exist and complete."""
        self.drill_data['year'] = input("[ENTER] - выйти."
                                        "\nВведите год: ")
        if not self.drill_data['year']:
            raise MainMenu
        print("Выберете месяц:")
        self.drill_data['month'] = super().choise_from_list(self.month_list)
        print("Выберете смену:")
        self.drill_data['shift'] = super().choise_from_list(
            Reports(self.user).shifts)

    def _bring_data_from_main_report(self):
        """Bring meters, result and rock mass from main_career_report."""
        main_report_results = Reports(self.user).give_main_results(
            self.drill_data['year'],
            self.drill_data['month'],
            self.drill_data['shift'])
        result_comlete = False
        if main_report_results and main_report_results[2] != 0:
            (self.drill_data['meters'],
             self.drill_data['result'],
             self.drill_data['rock_mass']) = main_report_results
            result_comlete = True
        return result_comlete

    def _save_drill_report_to_temp(self):
        """Save drill report to temp file, until main report be complete."""
        super().dump_data(
            data_path=self.temp_drill_path,
            base_to_dump=self.drill_data,
            user=self.user,
        )

    def _load_from_temp_drill(self):
        """Load data from temp drill file."""
        self.drill_data = super().load_data(
            data_path=self.temp_drill_path,
            user=self.user,
        )

    def _comlete_drill_report(self):
        """Complete drill report with meters, result
        and rock mass from main_career_report."""
        if self.temp_drill_path.exists():
            self._load_from_temp_drill()
            result_comlete = self._bring_data_from_main_report()
            if result_comlete:
                self._save_drill_report()
                os.remove(self.temp_drill_path)
                print("Temp Drill report completed.")

    def create_drill_report(self):
        """Create drill report"""
        self._input_year_month_shift()
        print("Введите данные по инструменту:")
        self._input_other_stats()
        results_exist = self._bring_data_from_main_report()
        super().clear_screen()
        self._check_correctly_input(results_exist)

    def show_statistic_by_year(self):
        """Showing statistic about drill instrument."""
        if isinstance(self.drill_file, pd.DataFrame):
            print("[ENTER] - выход"
                  "\nВыберете год:")
            year = super().choise_from_list(sorted(set(self.drill_file.year)),
                                            none_option=True)
        else:
            print("Статистик по буровому инструменту отстутствует.")
        if year:
            self._visualise_statistic(year)
        input('\n[ENTER] - выйти.')
