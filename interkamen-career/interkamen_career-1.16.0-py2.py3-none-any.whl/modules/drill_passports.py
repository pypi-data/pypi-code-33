#!/usr/bin/env python3.7
"""
Module to work with drill passports.

.give_dpassports_for_date() - give list of drill passports for given date.

.count_param_from_passports() - count totall drill meters for current driller
from passports.

.create_drill_passport() - create new drill passport.

.def edit_passport() - edit drill passport.
"""

from __future__ import annotations

from typing import Union, Dict, List
import pandas as pd
from numpy import nan as Nan
from .support_modules.dump_to_exl import DumpToExl
from .administration.logger_cfg import Logs
from .support_modules.custom_exceptions import MainMenu
from .support_modules.standart_functions import (
    BasicFunctionsS
    as BasF_S
)


LOGGER = Logs().give_logger(__name__)


class DPassportS(BasF_S):
    """Drill passport."""

    __slots__ = [
        'pass_number',
        'master',
        'params',
        'bareholes',
    ]

    horizonds = ['+108', '+114', '+120', '+126', '+132']

    def __init__(self, pass_number, master, empty_df, massive_type, rep_date):
        self.pass_number = pass_number
        self.master = master
        self.params = empty_df
        self.bareholes = {}
        self.params.massive_type = massive_type
        for item in rep_date:
            self.params[item] = rep_date[item]

    def __repr__(self):
        bareholes_table = '\nдлина, м  количество, шт'
        for key in self.bareholes:
            bareholes_table = (bareholes_table +
                               f"\n  {key}    -    {int(self.bareholes[key])}")
        output = (
            "Дата паспорта: {}"
            .format('.'.join(map(str, [
                self.params.year, self.params.month, self.params.day]))) +
            "\nНомер паспорта: {}; Тип взрыва: {}".format(
                int(self.params.number),
                str(self.params.massive_type)) +
            "\nГорный мастер: {}".format(str(self.params.master)) +
            "\nБурильщик: {}".format(str(self.params.driller)) +
            "\nГоризонт: {}".format(str(self.params.horizond)) +
            "\n\nПараметры блока:" +
            "\nОбъем блока: {}м.кб.".format(float(self.params.block_vol)) +
            "\nГабариты: {}м x {}м x {}м".format(*map(float, [
                self.params.block_width,
                self.params.block_height,
                self.params.block_depth])) +
            "\n\nПараметры взрывания:\n" +
            "Расход пороха: {}г/м.куб".format(int(self.params.pownd_consump)) +
            "\nКоличество пороха: {}кг".format(float(self.params.pownder)) +
            "\nКоличество ДШ: {}м".format(int(self.params.d_sh)) +
            "\nКоличество ЭД: {}шт.".format(int(self.params.detonators)) +
            "\n\nПараметры шпуров:" +
            "\nПробурено метров: {}м".format(round(
                float(self.params.totall_meters), 1)) +
            "\nКоличество шпуров: {}шт.".format(int(round(
                (self.params.block_width - 0.4) / 0.35, 0)))
            )
        output += bareholes_table
        output += "\n\nКоронки в скале: {}".format(
            int(self.params.bits_in_rock))
        return output

    @classmethod
    def _round_to_half(cls, number):
        number = (number // 0.5 * 0.5
                  if number % 0.5 < 0.29
                  else number // 0.5 * 0.5 + 0.5)
        return number

    def _input_bareholes(self):
        """Input totall bareholes."""
        print("\nВведите шпуры.\n"
              "Если вы хотите ввести несколько шпуров одной длины, \n"
              "введите их в следующем формате: колличество*длинна.\n"
              "Например: 6*5.5"
              "\n[e] - закончить ввод\n")
        totall_bareholes = 0
        totall_meters = 0
        temp_bareholes = {}
        while True:
            barehole = input("Введите значения шпуров: ")
            if barehole == '' and not temp_bareholes:
                continue
            if barehole in ['e', 'E', 'е', 'Е', '']:
                break
            elif '*' in barehole:
                barehole = barehole.split('*')
                bareholes_number = int(barehole[0])
                bar_lenght = super().float_input(inp=barehole[1])
                bars_lenghts = bar_lenght * bareholes_number
            elif barehole.isdigit():
                bareholes_number = 1
                bar_lenght = bars_lenghts = super().float_input(inp=barehole)
            else:
                print("Некорректный ввод.")
                continue
            totall_bareholes += bareholes_number
            totall_meters += bars_lenghts
            if bar_lenght in temp_bareholes:
                temp_bareholes[bar_lenght] += bareholes_number
            else:
                temp_bareholes[bar_lenght] = bareholes_number
        self.bareholes = temp_bareholes
        self.params.totall_meters = totall_meters
        return totall_bareholes

    def _set_horizond(self):
        """Choose horizond."""
        print("Выберете горизонт:")
        self.params.horizond = super().choise_from_list(self.horizonds)

    def _set_pownder_parametrs(self):
        """Set pownder."""
        # Pownder consumption:
        pownd_consump = int(input("Введите расход ДП в граммах: "))
        self.params.pownd_consump = pownd_consump
        # Detonators:
        self.params.detonators = int(input("Введите количество ЭД: "))

    def _set_driller(self, user):
        """Choose driller."""
        drillers_path = super().get_root_path() / 'data' / 'drillers'
        drillers = super().load_data(
            data_path=drillers_path,
            user=user,
        )
        print("Выберете бурильщика:")
        self.params.driller = super().choise_from_list(drillers)

    def _set_block_parametrs(self, bareholes_number):
        """Block parametrs (height, width, volume)"""
        block_height = super().float_input(msg="Введите высоту блока: ")
        self.params.block_height = block_height
        block_width = round(bareholes_number * 0.35 + 0.4, 1)
        self.params.block_width = block_width
        block_depth = self.params.totall_meters / bareholes_number
        self.params.block_depth = round(block_depth, 2)
        block_vol = round(block_height * block_width * block_depth, 1)
        self.params.block_vol = block_vol

    def _set_bits_in_rock(self):
        """Number of drill bits in rock."""
        bits_in_rock = input("Коронки в скале: ")
        if bits_in_rock:
            self.params.bits_in_rock = int(bits_in_rock)
        else:
            self.params.bits_in_rock = 0

    def _count_expl_volume(self, bareholes_number):
        """Count amounts of DH and pownder."""
        pownder = round(
            self.params.block_vol * self.params.pownd_consump / 1000, 1)
        self.params.pownder = self._round_to_half(pownder)
        d_sh = (
            float(self.params.totall_meters) + (bareholes_number * 0.3)
            + self.params.block_width + 30
        )
        self.params.d_sh = round(d_sh / 10, 0) * 10

    def _bareholes_and_dependencies(self):
        """Count bareholes parametrs and dependenses.
        (block param, expl vol)"""
        bareholes_number = self._input_bareholes()
        self._set_block_parametrs(bareholes_number)
        self._count_expl_volume(bareholes_number)

    def fill_passport(self, user):
        """Fill passport."""
        self.params.number = self.pass_number
        self.params.master = self.master
        self._set_horizond()
        self._set_pownder_parametrs()
        self._set_driller(user)
        self._bareholes_and_dependencies()
        self._set_bits_in_rock()

    def change_parametrs(self):
        """Change passport parametrs."""
        edit_menu_dict = {
            'Изменить горизонт': self._set_horizond,
            'Изменить расход ВВ и ЭД': self._set_pownder_parametrs,
            'Изменить бурильщика': self._set_driller,
            'Ввести новые длины шпуров': self._bareholes_and_dependencies,
            'Удалить паспорт': 'del',
            '[закончить редактирование]': 'exit'
        }
        while True:
            super().clear_screen()
            print(self.__repr__())
            print("\nВыберете пункт для редактирования:")
            action_name = super().choise_from_list(edit_menu_dict)
            if action_name in ['[закончить редактирование]', '']:
                break
            elif action_name == 'Удалить паспорт':
                if super().confirm_deletion('паспорт'):
                    self.params.number = None
                    break
            else:
                edit_menu_dict[action_name]()


class NPassportS(DPassportS):
    """Nongabarites passport."""

    __slots__ = ['nk_count']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nk_count = self._input_count()

    @classmethod
    def _input_count(cls):
        """Input NG count."""
        count = int(input("Введите число негабаритов: "))
        return count

    def __repr__(self):
        output = super().__repr__()
        output = output.replace(
            "\nГорный мастер:",
            f": {self.nk_count}шт.\nГорный мастер:")
        return output


class DrillPassports(BasF_S):
    """Class to create and working with drill passports."""

    __slots__ = [
        'drill_pass_path',
        'user',
        'drill_pass_file',
        'empty_serial',
        'empty_df',
    ]

    massive_type = ['Массив', 'Повторный', 'Негабариты']
    pass_columns = [
        'number', 'year', 'month', 'day', 'horizond', 'totall_meters',
        'driller', 'block_height', 'block_width', 'block_depth', 'block_vol',
        'pownd_consump', 'pownder', 'detonators', 'd_sh', 'master',
        'bits_in_rock', 'massive_type'
    ]

    def __init__(self, user):
        self.drill_pass_path = (
            super().get_root_path() / 'data' / 'drill_passports')
        self.user = user
        self._create_empty_df()
        if self.drill_pass_path.exists():
            self.drill_pass_file = super().load_data(
                data_path=self.drill_pass_path,
                user=user,
            )
        else:
            self.drill_pass_file = {}
            super().dump_data(
                data_path=self.drill_pass_path,
                base_to_dump=self.drill_pass_file,
                user=user,
            )

    @classmethod
    def _crerate_pass_date(cls, *, year: int, day: int, month: int) -> str:
        """Create date for passport name."""
        if month // 10 == 0:
            month = '0' + str(month)
        if day // 10 == 0:
            day = '0' + str(day)
        pass_date = "{}-{}-{}".format(year, month, day)
        return pass_date

    def _create_pass_name(self, passport: Union[DPassportS,
                                                NPassportS]) -> str:
        """Create passport name."""
        pass_date = self._crerate_pass_date(
            year=int(passport.params.year),
            month=int(passport.params.month),
            day=int(passport.params.day),
        )
        pass_name = (
            "{} №{}-{}".format(
                pass_date,
                int(passport.params.number),
                str(passport.params.massive_type),
            )
        )
        return pass_name

    def _create_empty_df(self):
        """Create blanc DF list."""
        self.empty_df = pd.DataFrame(columns=self.pass_columns)
        self.empty_serial = pd.Series(
            [Nan for name in self.pass_columns],
            index=self.pass_columns
        )

    def _check_if_report_exist(self,
                               rep_date: Dict[str, int],
                               number: str) -> bool:
        """Check if report exist in base"""
        check = True
        rep_date = self._crerate_pass_date(**rep_date)
        for report in self.drill_pass_file:
            if (rep_date == report.split(' ')[0] and
                    number == report.split(' ')[-1].split('-')[0][1:]):
                check = False
                print("Паспорт с этим номером уже существует.")
        return check

    def _save_or_not(self, passport: Union[NPassportS, DPassportS]):
        """Save passport or not."""
        save = input("\n[c] - сохранить паспорт: ")
        if save.lower() in ['c', 'с']:
            pass_name = self._create_pass_name(passport)
            print('\033[92m', pass_name, ' - cохранен.\033[0m')
            self.drill_pass_file[pass_name] = passport
            super().dump_data(
                data_path=self.drill_pass_path,
                base_to_dump=self.drill_pass_file,
                user=self.user,
            )
            LOGGER.warning(
                f"User '{self.user.login}' create drill pass.: {pass_name}"
            )
            exel = input("\nЖелаете создать exel файл? Y/N: ")
            if exel.lower() == 'y':
                if passport.__class__.__name__ == 'DPassportS':
                    DumpToExl().dump_drill_pass(passport)
                else:
                    DumpToExl().dump_drill_pass(passport,
                                                negab=passport.nk_count)
        else:
            print("Вы отменили сохранение.")

    def _choose_passport_from_bd(self):
        """Choose passport from BD."""
        years = {
            passp.split('-')[0]
            for passp in self.drill_pass_file
        }
        print("[ENTER] - выйти."
              "\nВыберете год:")
        year = super().choise_from_list(years, none_option=True)
        if not year:
            raise MainMenu
        months = {
            report.split('-')[1]
            for report in self.drill_pass_file
            if report.startswith(year)
        }
        print("Выберет месяц:")
        month = super().choise_from_list(months)
        if month:
            reports = [
                report
                for report in self.drill_pass_file
                if report.startswith('-'.join([year, month]))
            ]
            passport_name = super().choise_from_list(reports, none_option=True)

        return passport_name

    def _set_date(self) -> Dict[str, int]:
        """Set report date."""
        rep_date = super().input_date()
        day = int(input("Введите день: "))
        rep_date.update({'day': day})
        return rep_date

    def _last_number_of_passport(self):
        """Return last exist number."""
        last_passport = sorted(
            [passport for passport in self.drill_pass_file])[-1]
        last_number = last_passport.split(' ')[-1]
        return last_number

    def give_dpassports_for_date(self, pdate: str) -> List[DPassportS]:
        """Give list of drill passports for given date."""
        passports_list = [
            self.drill_pass_file[passport]
            for passport in self.drill_pass_file
            if self.drill_pass_file[passport].__class__.__name__ == 'DPassportS'
            and passport.split(' ')[0] == pdate
        ]
        return passports_list

    def count_param_from_passports(
            self,
            *,
            driller: str,
            rep_date: str,
            parametr: str,
    ) -> float:
        """Count totall meters for current driller."""
        paramert_totall = 0
        for passport in self.drill_pass_file:
            pas_file = self.drill_pass_file[passport]
            if (str(pas_file.params.driller) == driller and
                    passport.startswith(rep_date)):
                paramert_totall += round(float(pas_file.params[parametr]), 1)
        return paramert_totall

    def create_drill_passport(self):
        """Create drill passport."""
        if self.drill_pass_file:
            print("Номер последнего паспорта: ",
                  self._last_number_of_passport())
        rep_date = self._set_date()

        while True:
            number = input("\nВведите номер паспорта: ")
            if not number:
                raise MainMenu
            if self._check_if_report_exist(rep_date, number):
                break

        print("Выберете тип паспорта:")
        pass_type = super().choise_from_list(self.massive_type)
        if pass_type == 'Негабариты':
            pass_blanc = NPassportS
        else:
            pass_blanc = DPassportS
        passport = pass_blanc(
            pass_number=number,
            master=self.user.name,
            empty_df=self.empty_serial,
            massive_type=pass_type,
            rep_date=rep_date,
            )
        passport.fill_passport(self.user)
        super().clear_screen()
        print(passport)
        self._save_or_not(passport)

    def edit_passport(self):
        """Print passport for current number."""
        passport_name = self._choose_passport_from_bd()
        if not passport_name:
            raise MainMenu
        passport = self.drill_pass_file[passport_name]
        passport.change_parametrs()
        if not passport.params.number:
            self.drill_pass_file.pop(passport_name)
            super().dump_data(
                data_path=self.drill_pass_path,
                base_to_dump=self.drill_pass_file,
                user=self.user,
            )
            LOGGER.warning(
                f"User '{self.user.login}' delete drill pass.: "
                + f"{passport_name}"
            )
        else:
            self._save_or_not(passport)
