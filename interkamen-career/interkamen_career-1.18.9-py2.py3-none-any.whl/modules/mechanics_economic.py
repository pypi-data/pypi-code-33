#!/usr/bin/env python3

"""Visualise statistic by machine economic."""


from __future__ import annotations

import pandas as pd
from matplotlib import pyplot as plt
from typing import Dict
from .mechanic_report import MechReports
from .administration.logger_cfg import Logs
from .support_modules.custom_exceptions import MainMenu
from .support_modules.standart_functions import (
    BasicFunctionsS
    as BasF_S
)

LOGGER = Logs().give_logger(__name__)


class MechEconomic(MechReports):
    """Visualise statistic by machine economic."""

    __slots__ = (
        'mech_econ_path',
        'mech_econ_data',
        'mech_econ_file',
    )

    def __init__(self, user):
        """Load mech econom data."""
        super().__init__(user)
        self.mech_econ_data = {}
        self.mech_econ_path = (
            super().get_root_path() / 'data' / 'mech_ecomomic'
        )
        if self.mech_econ_path.exists():
            self.mech_econ_file = super().load_data(
                data_path=self.mech_econ_path,
                user=user,
            )
        else:
            self.mech_econ_file = pd.DataFrame(self.mech_econ_data, index=[0])

    def _save_mech_econom(self):
        """Save mech econom and create log file."""
        self.mech_econ_file = self.mech_econ_file.append(
            self.mech_econ_data,
            ignore_index=True
        )
        self._dump_mech_econ_data()
        self._log_mech_econ_creation()

    def _dump_mech_econ_data(self):
        """Dump salary data to file."""
        super().dump_data(
            data_path=self.mech_econ_path,
            base_to_dump=self.mech_econ_file,
            user=self.user,
        )

    def _log_mech_econ_creation(self):
        """Save log about salary creation."""
        report_name = '{}-{}'.format(
            self.mech_econ_data['year'],
            self.mech_econ_data['month'],
        )
        LOGGER.warning(
            f"User '{self.user.login}' create mechanic econom.: {report_name}"
        )

    def _visualise_one_day_cost(self):
        """Visualise cost of one day by each machine."""
        year = self._chose_year()
        data_by_year = super().give_dataframe_by_year(year)
        data_for_plot = {
            'mach': [],
            'day_cost': [],
        }
        for mach in super().maint_dict['mach_name']:
            totall_cost = sum(self.mech_econ_file[mach])
            total_work = sum(data_by_year.work)
            number_of_wdays = total_work
            day_cost = round(totall_cost/number_of_wdays, 0)
            data_for_plot['mach'].append(mach)
            data_for_plot['day_cost'].append(day_cost)
        data_for_plot = pd.DataFrame(data_for_plot)
        self._create_one_day_cost_plot(data_for_plot)

    def _input_machines_econ(self, mech_econ_date):
        """Input money, spent for machine in month."""
        self.mech_econ_data['year'] = mech_econ_date['year']
        self.mech_econ_data['month'] = mech_econ_date['month']
        super().clear_screen()
        print("Введите сумму для каждой техники:")
        for mach in super().maint_dict['mach_name']:
            self.mech_econ_data[mach] = float(input(f"{mach}: "))
        save = input(
            "\nДанные введены."
            "\n[s] - сохранить данные: "
        )
        if save.lower() == 's':
            self._save_mech_econom()
            print("Данные сохранены.")
        else:
            print("Вы отменили сохранение.")
        input("\n[ENTER] - выйти.")

    def _visualise_statistic(self, year):
        """Visualise statistic."""
        mech_econ_year = self.mech_econ_file.year == year
        data_by_year = (
            self.mech_econ_file[mech_econ_year]
            .sort_values(by=['month'])
        )
        super().print_all_dataframe(data_by_year)
        input("\n[ENTER] - выйти.")

    def _chose_year(self):
        """Show statistic about drill instrument."""
        print("[ENTER] - выход"
              "\nВыберете год:")
        year = super().choise_from_list(
            sorted(set(self.mech_econ_file.year)),
            none_option=True
        )
        if year:
            return year
        else:
            raise MainMenu

    @BasF_S.set_plotter_parametrs
    def _create_one_day_cost_plot(self, dataframe):
        """Create one day cost plot."""
        figure = plt.figure()

        x_cost = list(range(len(super().maint_dict['mach_name'])))

        axle = figure.add_subplot(111)
        axle.bar(
            x_cost, dataframe.day_cost, 0.3, alpha=0.4, color='r',
            label='Коэффициент', tick_label=dataframe.mach
        )
        axle.tick_params(labelrotation=90)
        axle.set_title(
            "Коэффициент целесообразности содержания техники руб/час. ",
            fontsize="x-large")
        axle.set_ylabel('руб.')
        axle.legend()
        axle.grid(
            True, linestyle='--', which='major',
            color='grey', alpha=.25, axis='y'
        )
        figure.tight_layout()
        plt.show()

    def create_mech_econom(self):
        """Create mechanic econom data report."""
        mech_econ_date = self.input_date()
        check = super().check_date_in_dataframe(
            self.mech_econ_file,
            mech_econ_date
        )
        if check:
            print("Данные за этот месяц уже внесены.")
            input("\n[ENTER] - выйти.")
        else:
            self._input_machines_econ(mech_econ_date)

    def show_econ_statistic(self, stat_variants: Dict):
        """Show machine economic statistic."""
        stat_variants = {
            'Целесообразность затрат на содержание техники.':
            self._visualise_one_day_cost,
        }
        print("[ENTER] - выйти."
              "\nВыберете вид отчета:")
        stat = super().choise_from_list(stat_variants, none_option=True)
        if stat:
            stat_variants[stat]()
