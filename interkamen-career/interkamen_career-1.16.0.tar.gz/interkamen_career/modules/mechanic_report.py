#!/usr/bin/env python3
"""
Mechanics reports.

.create_report() - create daily mechanics report for machines status.

.edit_report() - edit mechanics report.

.show_statistic(): - create plot with machine stats.

.maintenance_calendar() - create maintenance calendar.

.walk_thrue_maint_calendar() - working with maintainence calendar.
"""

from datetime import date
from operator import sub, add

import pandas as pd
from matplotlib import pyplot as plt

from .administration.logger_cfg import Logs
from .support_modules.custom_exceptions import MainMenu
from .support_modules.standart_functions import (
    BasicFunctionsS
    as BasF_S
)


LOGGER = Logs().give_logger(__name__)


class MechReports(BasF_S):
    """
    Class to work with statistic of machine maintainence.
    """

    __slots__ = ['mech_path', 'maint_path', 'user', 'temp_df', 'mech_file',
                 'mech_data', 'machines', 'maint_path', 'maint_file']

    machine_list = {
        'Хоз. Машина': ['УАЗ-390945', 'УАЗ-220695', 'ГАЗ-3307'],
        'Буровая': ['Commando-110', 'Commando-120'],
        'Погрузчик': ['Komazu-WA470', 'Volvo-L150'],
        'Кран': ['КС-5363А', 'КС-5363Б', 'КС-5363Б2 '],
        'Компрессор': ['AtlasC-881', 'AtlasC-882'],
        'Экскаватор': ['Hitachi-350', 'Hitachi-400'],
        'Самосвал': ['КрАЗ-914', 'КрАЗ-413', 'КрАЗ-069'],
        'Бульдозер': ['Бул-10'],
        'Дизельная эл. ст.': ['ДЭС-AD']
    }
    columns = ['year', 'month', 'day', 'mach_type', 'mach_name',
               'st_plan', 'st_acs', 'st_sep', 'work', 'notes']
    maint_dict = {
        'mach_name': [
            'УАЗ-390945', 'УАЗ-220695', 'ГАЗ-3307', 'Commando-110',
            'Commando-120', 'Komazu-WA470', 'Volvo-L150', 'КС-5363А',
            'КС-5363Б', 'КС-5363Б2 ', 'AtlasC-881', 'AtlasC-882',
            'Hitachi-350', 'Hitachi-400', 'КрАЗ-914', 'КрАЗ-413',
            'КрАЗ-069', 'Бул-10', 'ДЭС-AD'],
        'cycle': [400, 400, 400, 250,
                  250, 250, 250, 400,
                  400, 400, 250, 250,
                  250, 250, 400, 400,
                  400, 500, 60],
        'hours_pass': ['0' for x in range(19)],
    }

    def __init__(self, user):
        self.mech_data = {}
        self.mech_path = super().get_root_path() / 'data' / 'mechanics_report'
        self.maint_path = super().get_root_path() / 'data' / 'maintainence'
        self.user = user
        self.temp_df = pd.DataFrame()
        # Try to load mech reports file.
        if self.mech_path.exists():
            self.mech_file = super().load_data(
                data_path=self.mech_path,
                user=user,
            )

        else:
            self.mech_file = pd.DataFrame(self.mech_data, index=[0])
            super().dump_data(
                data_path=self.mech_path,
                base_to_dump=self.mech_file,
                user=user,
            )
        if 'mach_name' in self.mech_file:
            self.machines = sorted(set(self.mech_file.mach_name))
        # Try to load maintainence file.
        if self.maint_path.exists():
            self.maint_file = super().load_data(
                data_path=self.maint_path,
                user=user,
            )
        else:
            self.maint_file = self._create_blanc_maint()

    @classmethod
    def _check_hours_input(cls, hours):
        """Check input hours are correct"""
        hours = hours.split('-')
        try:
            correct = sum(list(map(int, hours))) < 13 and len(hours) == 4
        except ValueError:
            correct = False
        except IndexError:
            correct = False
        return correct

    @classmethod
    def _create_coeff_compare(cls, fig_plot, coefs, labels, title):
        """Create plot for compare KTG by shifts."""
        x_ktg = list(range(len(labels[0])))
        x_kti = [x - 0.35 for x in x_ktg]

        axle = fig_plot[0].add_subplot(fig_plot[1])
        axle.barh(x_ktg, coefs[0], 0.35, alpha=0.4, color='b',
                  label=labels[1], tick_label=labels[0])
        axle.barh(x_kti, coefs[1], 0.35, alpha=0.4, color='g',
                  label=labels[2])
        axle.set_title(title)
        axle.set_xlabel('%')
        axle.legend()
        axle.grid(True, linestyle='--', which='major',
                  color='grey', alpha=.25, axis='x')

    @classmethod
    def _select_machine(cls, choise, dataframe):
        """Select machine from data frame."""
        machine = list(dataframe.mach_name)[int(choise)]
        select_mach = dataframe['mach_name'] == machine
        print('\n', '\033[92m', machine, '\033[0m')
        return select_mach

    @classmethod
    def _check_maintenance_alarm(cls, check, machine, counter):
        """Check, if it is time to maintaine machine."""
        header = ''
        if not check.isnull().any() and int(counter) <= 0:
            header = (
                '\n\033[91mПодошло ТО для:\033[0m ' + machine +
                ' дата последнего ТО: ' + check.values[0]
            )
        return header

    def _start_maintainance(self, select_mach):
        """Start or reset maintainence of mach."""
        current_date = str(date.today())
        self.maint_file.loc[
            select_mach, 'last_maintain_date'] = current_date
        self.maint_file.loc[
            select_mach, 'hours_pass'] = self.maint_file.loc[
                select_mach, 'cycle']
        super().dump_data(
            data_path=self.maint_path,
            base_to_dump=self.maint_file,
            user=self.user,
        )

    def _create_blanc_maint(self):
        """Crete new maintenance DF."""
        maint_df = pd.DataFrame(
            self.maint_dict, columns=['mach_name', 'cycle',
                                      'last_maintain_date', 'hours_pass'])
        super().dump_data(
            data_path=self.maint_path,
            base_to_dump=maint_df,
            user=self.user,
        )
        return maint_df

    def _create_blanc(self, rep_date):
        """Create blanc for report."""
        for mach_type in self.machine_list:
            for mach_name in self.machine_list[mach_type]:
                self.mech_data['year'] = rep_date['year']
                self.mech_data['month'] = rep_date['month']
                self.mech_data['day'] = rep_date['day']
                self.mech_data['mach_type'] = mach_type
                self.mech_data['mach_name'] = mach_name
                self.mech_data['st_plan'] = 0
                self.mech_data['st_acs'] = 0
                self.mech_data['st_sep'] = 0
                self.mech_data['work'] = 0
                self.mech_data['notes'] = ''
                self.temp_df = self.temp_df.append(self.mech_data,
                                                   ignore_index=True)
        self.temp_df = self.temp_df[self.columns]

    def _input_hours(self):
        """Input hours."""
        check_input = False
        while not check_input:
            h_data = input(
                "Введите часы через тире\n\tПлан-Авар-Зап-Раб: ")
            check_input = self._check_hours_input(h_data)
            if not check_input:
                print("Необходимо ввести 4 числа, сумма которых не более 12!")
        h_data = list(map(int, h_data.split('-')))
        return h_data

    def _add_hours_to_mach(self, select_mach, hours_data):
        """Add hous to machine."""
        for item in ['st_plan', 'st_acs', 'st_sep', 'work']:
            self.temp_df.loc[select_mach, item] = hours_data[0]
            hours_data = hours_data[1:]

    def _add_note_to_mach(self, select_mach):
        """Add note to mach."""
        note = input("Введите примечание: ")
        self.temp_df.loc[select_mach, 'notes'] = note

    def _save_report(self):
        """Save daily report to base."""
        if self.mech_file.empty:
            self.mech_file = self.temp_df
        else:
            self.mech_file = self.mech_file.append(self.temp_df)
        self.walk_thrue_maint_calendar(sub)
        super().dump_data(
            data_path=self.mech_path,
            base_to_dump=self.mech_file,
            user=self.user,
        )

    def _stat_by_period(self, *stand_reason, month):
        print("Выберете год:")
        year = super().choise_from_list(sorted(set(self.mech_file.year)))
        if month:
            print("Выберете месяц:")
            data_by_year = self.mech_file[self.mech_file.year == year]
            month = super().choise_from_list(sorted(set(data_by_year.month)))
        if stand_reason:
            self._visualise_reasons_stat(year, month)
        else:
            self._visualise_stat(year, month)

    def _visualise_reasons_stat(self, year, month):
        """Visualise stats by reasons."""
        period_base = self._count_data_for_period(year, month, reason=True)
        period_reasons_df = self._create_reasons_df(period_base)
        self._create_reasons_plot(period_reasons_df)

    def _visualise_stat(self, year, month):
        """Visualisate statistic."""
        coeff_dfs = self._create_coefficient_df(year, month)
        self._create_plot(*coeff_dfs)

    def _create_coefficient_df(self, year, month):
        """Create coefficient dataframes for period."""
        period_base, shift1_base, shift2_base = self._count_data_for_period(
            year, month, reason=None)
        period_coef_df = self._create_coef_df(period_base)
        shift1_coef_df = self._create_coef_df(shift1_base)
        shift2_coef_df = self._create_coef_df(shift2_base)
        return period_coef_df, shift1_coef_df, shift2_coef_df

    def give_average_shifs_kti(self, year, month):
        """Give average shifts KTI for month."""
        kti_dict = {'критерий': 'kti'}
        coeff_dfs = self._create_coefficient_df(year, month)
        shift1_df, shift2_df = coeff_dfs[1:]
        kti_dict['Смена 1'] = round(shift1_df.kti.mean(), 1)
        kti_dict['Смена 2'] = round(shift2_df.kti.mean(), 1)
        return kti_dict

    def _create_reasons_df(self, curr_base):
        """Create coef DF for cerrent period."""
        temp_reasons_list = {
            'mach': [],
            'sum_plan': [],
            'sum_acs': [],
            'sum_sep': []
        }
        for mach in self.machines:
            mach_period = curr_base[curr_base.mach_name == mach]
            sum_plan = sum(mach_period.st_plan)
            sum_acs = sum(mach_period.st_acs)
            sum_sep = sum(mach_period.st_sep)
            temp_reasons_list['mach'].append(mach)
            temp_reasons_list['sum_plan'].append(sum_plan)
            temp_reasons_list['sum_acs'].append(sum_acs)
            temp_reasons_list['sum_sep'].append(sum_sep)
        reasons_df = pd.DataFrame(temp_reasons_list)
        return reasons_df

    def _create_coef_df(self, curr_base):
        """Create coef DF for cerrent period."""
        temp_coef_list = {
            'mach': [],
            'ktg': [],
            'kti': [],
            'rel_kti': []
        }
        for mach in self.machines:
            mach_period = curr_base[curr_base.mach_name == mach]
            kalendar_time = mach_period.shape[0] * 12
            stand_time = sum(
                mach_period.st_plan + mach_period.st_sep + mach_period.st_acs)
            avail_time = kalendar_time - stand_time
            if kalendar_time:
                ktg = avail_time / kalendar_time * 100
            else:
                ktg = 0
            if avail_time:
                kti = sum(mach_period.work) / avail_time * 100
            else:
                kti = 0
            rel_kti = ktg / 100 * kti
            temp_coef_list['mach'].append(mach)
            temp_coef_list['ktg'].append(round(ktg, 1))
            temp_coef_list['kti'].append(round(kti, 1))
            temp_coef_list['rel_kti'].append(round(rel_kti, 1))
        coef_df = pd.DataFrame(temp_coef_list)
        return coef_df

    @BasF_S.set_plotter_parametrs
    def _create_reasons_plot(self, reasons_df):
        """Create statistic by reasons plots."""
        figure = plt.figure()

        x_plan = list(range(len(self.machines)))
        x_acs = [x + 0.3 for x in x_plan]
        x_sep = [x + 0.3 for x in x_acs]

        axle = figure.add_subplot(111)
        axle.bar(x_plan, reasons_df.sum_plan, 0.3, alpha=0.4, color='b',
                 label='Плановый ремонт')
        axle.bar(x_acs, reasons_df.sum_acs, 0.3, alpha=0.4, color='r',
                 label='Аварийный ремонт', tick_label=reasons_df.mach)
        axle.tick_params(labelrotation=90)
        axle.bar(x_sep, reasons_df.sum_sep, 0.3, alpha=0.4, color='g',
                 label='Ожидание запчастей')
        axle.set_title("Причины простоев.", fontsize="x-large")
        axle.set_ylabel('часы')
        axle.legend()
        axle.grid(True, linestyle='--', which='major',
                  color='grey', alpha=.25, axis='y')
        figure.tight_layout()
        plt.show()

    def _create_short_mach_names(self):
        """ Create compact machine names."""
        short_mach = [x[:3]+' '+x[-3:] for x in self.machines]
        return short_mach

    @BasF_S.set_plotter_parametrs
    def _create_plot(self, period_coef_df, shift1_coef_df, shift2_coef_df):
        """Create statistic plots."""
        short_mach = self._create_short_mach_names()
        figure = plt.figure()
        suptitle = figure.suptitle("Ремонты техники.", fontsize="x-large")
        self._create_coeff_compare(
            (figure, 131),
            labels=(period_coef_df.mach, 'КТГ', 'КТИ'),
            title='КТГ и КТИ за выбранный период.',
            coefs=(period_coef_df.ktg, period_coef_df.rel_kti)
            )
        self._create_coeff_compare(
            (figure, 132),
            labels=(short_mach, 'Бригада 1', 'Бригада 2'),
            title='Сравнительные КТИ бригад.',
            coefs=(shift1_coef_df.kti, shift2_coef_df.kti)
            )
        self._create_coeff_compare(
            (figure, 133),
            labels=(short_mach, 'Бригада 1', 'Бригада 2'),
            title='Сравнительные КТГ бригад.',
            coefs=(shift1_coef_df.ktg, shift2_coef_df.ktg)
            )
        figure.tight_layout()
        suptitle.set_y(0.95)
        figure.subplots_adjust(top=0.85)
        plt.show()

    def _count_data_for_period(self, year, month, reason):
        """Create data frames for current period)"""
        if month:
            period_base = self.mech_file[
                (self.mech_file.year == year) & (self.mech_file.month == month)
                ]
        else:
            period_base = self.mech_file[(self.mech_file.year == year)]
        if not reason:
            shift1_base = period_base[period_base.day < 16]
            shift2_base = period_base[period_base.day > 15]
            data = (period_base, shift1_base, shift2_base)
        else:
            data = period_base
        return data

    def _working_with_report(self, rep_date):
        """Edit report."""
        while True:
            super().clear_screen()
            print('{}.{}.{}'.format(*map(int, rep_date.values())))
            print(self.temp_df[
                ['mach_name', 'st_plan', 'st_acs', 'st_sep', 'work', 'notes']
                ])
            choise = input("\n[d] - выйти и \033[91mУДАЛИТЬ\033[m данные."
                           "\n[s] - \033[92mСОХРАНИТЬ\033[0m отчет.\n"
                           "\nВыберете технику для внесения данных: ")
            if choise.lower() == 's':
                self._save_report()
                LOGGER.warning(
                    f"User '{self.user.login}' create mechanics report: "
                    + '{year}.{month}.{day}'.format(**rep_date)
                )
                print("\n\033[92mДанные сохранены.\033[0m")
                input('\n[ENTER] - выйти.')
                break
            elif choise.lower() == 'd':
                confirm = super().confirm_deletion('отчет')
                if confirm:
                    input('\n[ENTER] - выйти.')
                    break
                continue
            elif not choise.isdigit():
                continue
            elif int(choise) > 18:
                continue
            select_mach = self._select_machine(choise, self.temp_df)
            hours_data = self._input_hours()
            self._add_hours_to_mach(select_mach, hours_data)
            self._add_note_to_mach(select_mach)

    def _make_day_report_temp(self, rep_date):
        """Make report of day temr and drop it from DF."""
        self.temp_df = self.mech_file[
            (self.mech_file['year'] == rep_date['year']) &
            (self.mech_file['month'] == rep_date['month']) &
            (self.mech_file['day'] == rep_date['day'])
            ]
        self.walk_thrue_maint_calendar(add)
        self.mech_file = self.mech_file.append(
            self.temp_df).drop_duplicates(keep=False)
        super().dump_data(
            data_path=self.mech_path,
            base_to_dump=self.mech_file,
            user=self.user,
        )

    def _add_hours_to_maint_counter(self, oper, check,
                                    add_hours, maint_mach):
        """Add or minus hours from maintenance counter in calendar."""
        if not check.isnull().any():
            self.maint_file.loc[maint_mach, 'hours_pass'] = oper(
                int(self.maint_file.loc[maint_mach, 'hours_pass']),
                int(add_hours)
                )
            super().dump_data(
                data_path=self.maint_path,
                base_to_dump=self.maint_file,
                user=self.user,
            )

    def create_report(self):
        """Create daily report."""
        while True:
            rep_date = super().input_date()
            if not rep_date:
                break
            check = super().check_date_in_dataframe(self.mech_file, rep_date)
            day = input("\nВведите день: ")
            if not day:
                raise MainMenu
            rep_date.update({'day': int(day)})
            check = super().check_date_in_dataframe(self.mech_file, rep_date)
            if check:
                print("Отчет за это число уже существует.")
            else:
                self._create_blanc(rep_date)
                self._working_with_report(rep_date)
                break

    def edit_report(self):
        """Show report for current date."""
        print("[ENTER] - выйти."
              "\nВыберете год:")
        year = super().choise_from_list(sorted(set(self.mech_file.year)))
        if not year:
            raise MainMenu
        print("Выберете месяц:")
        data_by_year = self.mech_file[self.mech_file.year == year]
        month = super().choise_from_list(sorted(set(data_by_year.month)))
        av_days = set(sorted(data_by_year[data_by_year.month == month].day))

        print("Доступные даты:\n\t",
              super().colorise_avaliable_date(int(year), int(month), av_days))

        day = input("Введите день: ")
        if day:
            rep_date = {
                'year': int(year),
                'month': int(month),
                'day': int(day),
            }
            self._make_day_report_temp(rep_date)
            self._working_with_report(rep_date)

    def show_statistic(self, *stand_reason):
        """
        Show statistic for mechanics report. If no stand_reason arg, it'll
        show coefficient stat, if are - stand reason comparison.
        """
        stat_variants = {
            'Месячная статистика':
            lambda *arg: self._stat_by_period(*arg, month=True),
            'Годовая статистика':
            lambda *arg: self._stat_by_period(*arg, month=None)
        }
        print("[ENTER] - выйти."
              "\nВыберете вид отчета:")
        stat = super().choise_from_list(stat_variants, none_option=True)
        if stat:
            stat_variants[stat](*stand_reason)

    def maintenance_calendar(self):
        """Work with maintenance calendar."""
        while True:
            super().clear_screen()
            print(self.maint_file)
            choise = input("\n[e] - выйти.\n"
                           "\nВыберете технику для обслуживания: ")
            if choise.lower() in ['e', 'е']:
                break
            elif not choise.isdigit():
                continue
            elif int(choise) > 18:
                continue
            select_mach = self._select_machine(choise, self.maint_file)
            self._start_maintainance(select_mach)
            input("обслуживание проведено.")

    def walk_thrue_maint_calendar(self, oper=None):
        """Work with maintaine calendar.
        oper - is a flag to do operations (add hours) with maint calendar.
        if None method only check maintenance count."""
        header = ''
        for machine in set(self.maint_file.mach_name):
            if not self.temp_df.empty:
                temp_mach = self.temp_df.mach_name == machine
                add_hours = self.temp_df.loc[temp_mach, 'work']
            maint_mach = self.maint_file.mach_name == machine
            check = self.maint_file.loc[maint_mach, 'last_maintain_date']
            counter = self.maint_file.loc[maint_mach, 'hours_pass']
            if oper:
                self._add_hours_to_maint_counter(oper, check,
                                                 add_hours, maint_mach)
            else:
                header += self._check_maintenance_alarm(
                    check, machine, counter)
        return header
