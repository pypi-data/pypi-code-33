#!/usr/bin/env python3
"""
This module contain class that provide working with brigade rating.

.give_rating() - give rating to brigade from current user.

.count_brigade_winner() - count brigade winner for current month.
"""

from copy import deepcopy
import pandas as pd
from .mechanic_report import MechReports
from .main_career_report import Reports
from .administration.logger_cfg import Logs
from .support_modules.custom_exceptions import MainMenu
from .support_modules.standart_functions import (
    BasicFunctionsS
    as BasF_S
)


LOGGER = Logs().give_logger(__name__)


class Rating(BasF_S):
    """Working with ratings in DataFrame."""

    __slots__ = ['brig_rating_path', 'totl_res', 'user',
                 'temp_res', 'brig_rating_file']

    brig_columns = ['year', 'month', 'shift', 'cleanness', 'discipline',
                    'roads', 'maintain', 'user']
    shifts = ['Смена 1', 'Смена 2']


    def __init__(self, user):
        self.temp_res = {
            'критерий': [],
            'Смена 1': [],
            'Смена 2': []
        }
        self.brig_rating_path = (
            super().get_root_path() / 'data' / 'brig_rating')
        self.user = user
        self.totl_res = deepcopy(self.temp_res)
        if self.brig_rating_path.exists():
            self.brig_rating_file = super().load_data(
                data_path=self.brig_rating_path,
                user=user,
            )
        else:
            self.brig_rating_file = pd.DataFrame(columns=self.brig_columns)
            super().dump_data(
                data_path=self.brig_rating_path,
                base_to_dump=self.brig_rating_file,
                user=user,
            )

    def _create_rating(self, user, year, month, shift):
        """Create rating record."""
        super().clear_screen()
        rating_name = "{}.{} {}".format(year, month, shift)
        print(rating_name,
              "\nВыставите оценки по по десятибальной "
              "шкале по следующим критериям:")
        tmp_rating = {
            'year': year,
            'month': month,
            'shift': shift,
            'user': user.split(' ')[0]
        }
        directions = {
            'discipline': "Дисциплина: ",
            'cleanness': "Чистота забоя: ",
            'roads': "Содержание дорог и отвалов: ",
            'maintain': "Обслуживание техники: "
        }
        for direction in directions:
            while True:
                rating = input(directions[direction])
                check = super().check_number_in_range(rating, list(range(10)))
                if check:
                    tmp_rating[direction] = int(rating)
                    break
        confirm = input("\n[s] - сохранить оценки."
                        "\nПроверьте правильность введенных данных: ")
        if confirm.lower() == 's':
            self._save_rating(tmp_rating)
            LOGGER.warning(
                f"User '{self.user.login}' give rating: {rating_name}"
            )

    def _save_rating(self, tmp_rating):
        """Save temp rating to data frame."""
        self.brig_rating_file = self.brig_rating_file.append(
            tmp_rating, ignore_index=True)
        super().dump_data(
            data_path=self.brig_rating_path,
            base_to_dump=self.brig_rating_file,
            user=self.user,
        )
        print("\033[92mОценки сохранены.\033[0m")

    def _show_rating(self):
        """Choose date to show."""
        print("[ENTER] - выйти."
              "\nВыберете год:")
        year = super().choise_from_list(
            sorted(set(self.brig_rating_file.year)),
            none_option=True,
        )
        if not year:
            raise MainMenu
        print("Выберете месяц:")
        data_by_year = self.brig_rating_file[
            self.brig_rating_file.year == year]
        month = super().choise_from_list(
            sorted(set(data_by_year.month)),
            none_option=True,
        )
        if not month:
            raise MainMenu
        super().clear_screen()
        columns = ['shift', 'cleanness', 'discipline',
                   'roads', 'maintain', 'user']
        data_by_month = data_by_year[data_by_year.month == month]
        print("{}.{}\n".format(year, month),
              data_by_month[columns])
        return year, month, data_by_month

    def _count_average_rating(self, data_by_month):
        """Count average rating from users rating."""
        data_by_month = data_by_month.drop(columns=['year', 'month', 'user'])
        for column in data_by_month.drop(columns='shift'):
            self.totl_res['критерий'].append(column)
            for shift in self.shifts:
                result = data_by_month[data_by_month['shift'] == shift].drop(
                    columns='shift')
                self.totl_res[shift].append(round(result[column].mean(), 1))

    def _add_main_brigades_results(self, year, month):
        """Add main brigades results from Main Report to average rating."""
        self.totl_res['критерий'].extend(['result', 'rock_mass'])
        for shift in self.shifts:
            brig_results = Reports(self.user).give_main_results(
                str(year), str(month), shift)
            if brig_results:
                self.totl_res[shift].extend(brig_results[1:])
            else:
                self.totl_res[shift].extend([0, 0])

    def _add_average_kti(self, year, month):
        """Add average kti from Mechanic Report to average rating."""
        self.totl_res = pd.DataFrame(self.totl_res)
        brigades_kti = (
            MechReports(self.user)
            .give_average_shifs_kti(year, month)
        )
        self.totl_res = self.totl_res.append(brigades_kti, ignore_index=True)

    def _count_wining_points(self):
        """Count winner."""
        point1 = point2 = 0
        for reason in self.totl_res['критерий']:
            row = self.totl_res['критерий'] == reason
            shift1_item = float(self.totl_res.loc[row, 'Смена 1'])
            shift2_item = float(self.totl_res.loc[row, 'Смена 2'])
            if shift1_item > shift2_item:
                point1 += 1
            else:
                point2 += 1
        print("\n          Итог:    {}        {}".format(point1, point2))

    def give_rating(self):
        """Give rating to shift."""
        while True:
            rep_date = super().input_date()
            if not rep_date:
                break
            check = super().check_date_in_dataframe(
                self.brig_rating_file, rep_date)
            print("Выберете смену:")
            shift = super().choise_from_list(self.shifts)
            rep_date.update({
                'shift': shift,
                'user': self.user.name.split(' ')[0]
                })
            check = super().check_date_in_dataframe(
                self.brig_rating_file, rep_date)
            if check:
                super().clear_screen()
                print("Вы уже выставляли оценки за этот период.")
            else:
                self._create_rating(**rep_date)
                break

    def count_brigade_winner(self):
        """Show rating."""
        users_rating = self._show_rating()
        self._count_average_rating(users_rating[-1])
        self._add_main_brigades_results(*users_rating[:-1])
        self._add_average_kti(*users_rating[:-1])
        print('\n', self.totl_res)
        self._count_wining_points()
        input('\n[ENTER] - выйти.')
