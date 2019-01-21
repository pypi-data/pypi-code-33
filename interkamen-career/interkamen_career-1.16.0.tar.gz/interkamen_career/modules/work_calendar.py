#!/usr/bin/env python3
"""
Working calendar module.

.create_calendar() - create calendar of workers shifts for current year.

.show_year_shifts() - show shift calendar by year.

.give_current_brigade() - give brigade for current date.

.give_current_itr() - give ITR for current date.

.give_current_month_shifts() - give shifts days for current month.
"""

import calendar as cl
from typing import Tuple, List
from .support_modules.custom_exceptions import MainMenu
from .support_modules.standart_functions import (
    BasicFunctionsS
    as BasF_S
)


class WCalendar(BasF_S):
    """Career working calendar ofr current year."""

    __slots__ = [
        'year',
        'working_days_in_month',
        'month_prnt',
        'month_length',
        'br_cal',
        'itr_cal',
    ]

    def __init__(self, year: int):
        self.month_prnt = ''
        self.year = year
        shifts = ["Смена 1", "Смена 2"]
        print("Выберете смену БРИГАДЫ"
              f", которая будет длинной в январе {year} года:")
        br_long = super().choise_from_list(shifts)
        print("Выберете смену ИТР"
              f", которая будет длинной в январе {year} года:")
        itr_long = super().choise_from_list(shifts)

        self.working_days_in_month = []
        self.month_length = []
        self.br_cal = self._set_cal(year=year,
                                    whos_long=br_long,
                                    workers="brig")
        self.itr_cal = self._set_cal(year=year,
                                     whos_long=itr_long,
                                     workers="itr")

    def __repr__(self):
        year = str(self.year)
        output = ('\n\t\t      \033[4mКалендарь пересменок \033[96m{}\033[0m.'
                  .format(year)) + '\n\n'
        for tripl_month in range(0, 12, 3):
            for month in range(tripl_month, tripl_month+3):
                self._colorized_month(month)
                month_end = self._count_end_spaces(month)
                tmp_month = list(self.month_prnt.split('\\n'))[:-1]
                tmp_month[-1] = tmp_month[-1] + month_end
                if len(tmp_month) == 7:
                    tmp_month.append(' '*20)
                if month in [4, 6]:
                    tmp_month[0] = tmp_month[0] + '    '
                if month in [0, 3, 6, 9]:
                    month_sum = tmp_month[:]
                else:
                    month_sum = [s1 + '\t' + s2
                                 for s1, s2 in zip(month_sum, tmp_month)]
            output += '\n'.join(month_sum) + '\n\n'
            month_sum = []
        output = output.replace(' ' + year, '     ')
        output += ("\033[93m*7\033[0m - пересменки ИТР\n"
                   + "\033[96m*31\033[0m - пересменки бригады.")
        return output

    @classmethod
    def _coin(cls, start: bool) -> bool:
        """Simple closures function that return True/False alternately."""
        stat = start

        def change():
            """Change coin state."""
            nonlocal stat
            tmp_stat = stat
            stat = not stat
            return tmp_stat
        return change

    def _set_cal(
            self,
            *,
            year: int,
            whos_long: str,
            workers: str,
    ) -> List[Tuple[int]]:
        self._calculate_same_or_dif(year)
        changes_dates = self._count_changes_dates(whos_long, workers)
        return changes_dates

    def _calculate_same_or_dif(self, year: int):
        """Calculate same or diff shift lenght in month."""
        cal = cl.TextCalendar()
        for month in range(1, 12):
            days = [day for day in cal.itermonthdays(year, month) if day != 0]
            self.month_length.append(len(days))
            if len(days) % 2 != 0:
                self.working_days_in_month.append('diff')
            else:
                self.working_days_in_month.append('same')
        # In december both brigades have same days.
        self.working_days_in_month.append('same')
        self.month_length.append(30)

    def _count_changes_dates(self, whos_long: str,
                             workers: str) -> List[Tuple[int]]:
        """Count changes days in months."""
        changes_dates = []
        if whos_long == 'Смена 1':
            first_long = self._coin(True)
        else:
            first_long = self._coin(False)

        for month in range(0, 12):
            if self.working_days_in_month[month] == 'diff':
                add_day = 1 if first_long() else 0
            else:
                add_day = 0
            changes_dates.append(self._begin_and_end(workers, month, add_day))
        return changes_dates

    def _begin_and_end(self,
                       workers: str,
                       month: int,
                       add_day: int) -> Tuple[int]:
        """Create shifts begin and end dates."""
        if workers == "brig":
            begin = 1
            end = self.month_length[month] // 2 + 1 + add_day
            # January holydays fix.
            if month == 0:
                begin = 3
                end = end + 1
        elif workers == "itr":
            begin = 7
            end = self.month_length[month] // 2 + 7 - add_day
            # January holydays fix.
            if month == 0:
                begin = begin + 2
                end = end + 2
        return begin, end

    def _count_end_spaces(self, month: int) -> str:
        """Count spaces at the end of month."""
        cal = cl.TextCalendar()
        days = [
            day
            for day in cal.itermonthdays(self.year, month + 1)
        ]
        month_end = -1
        day = 0
        while not day:
            day = days[-1]
            month_end += 1
            days = days[:-1]
        month_end = month_end * '   '
        return month_end

    def _colorized_days_in_text(self, days: Tuple[int], color: str):
        """Colorize days in calendar."""
        for day in days:
            st_day = str(day)
            if len(st_day) == 1:
                st_day = ' ' + st_day
            self.month_prnt = self.month_prnt.replace(
                st_day, color + st_day + '\033[0m', 1)

    def _colorized_days_in_html(self, days: Tuple[int], color: str):
        """Colorised days in html calendar."""
        for day in days:
            st_day = str(day)
            self.month_prnt = self.month_prnt.replace(
                f'>{st_day}<', f' style="color:{color}"><b>{st_day}</b><', 1)

    def _colorized_month(self, month: int, cal_format='text'):
        """Colorize month."""
        if cal_format == 'text':
            cal = cl.TextCalendar()
            self.month_prnt = cal.formatmonth(self.year, month+1).__repr__()
            function = self._colorized_days_in_text
            color_br = '\033[96m'
            color_itr = '\033[93m'
        elif cal_format == 'html':
            cal = cl.HTMLCalendar()
            self.month_prnt = cal.formatmonth(self.year, month+1)
            function = self._colorized_days_in_html
            color_br = 'green'
            color_itr = 'blue'
        function(self.br_cal[month], color_br)
        function(self.itr_cal[month], color_itr)

    def give_month_shifts(self, month: int, cal_format='text'):
        """Print calendar.
        format = text/html"""
        self._colorized_month(month, cal_format)
        if cal_format == 'text':
            self.month_prnt = self.month_prnt.replace('\\n', '\n\t')
            self.month_prnt = self.month_prnt.replace("'", '')
            curr_month_shifts = (
                self.month_prnt +
                "\n\t\033[93m*пересменка ИТР\033[0m" +
                "\n\t\033[96m*пересменка бригад\033[0m "
            )
        elif cal_format == 'html':
            curr_month_shifts = (
                self.month_prnt +
                '<p></p><p style="color:blue">*пересменка ИТР</p>' +
                '<p style="color:green">*пересменка бригад</p>'
            )
        return curr_month_shifts


class WorkCalendars(BasF_S):
    """Manage calendars."""

    __slots__ = [
        'calendar_path',
        'calendar_file',
        'user'
    ]

    def __init__(self, user):
        self.user = user
        self.calendar_path = (
            super().get_root_path() / 'data' / 'working_calendar')
        self.calendar_file = {}
        if self.calendar_path.exists():
            self.calendar_file = super().load_data(
                data_path=self.calendar_path,
                user=self.user,
            )

    def create_calendar(self):
        """Create working calendar."""
        year = input("Введите год: ")
        if not year.isdigit():
            raise MainMenu
        year = int(year)
        work_calendar = WCalendar(year)
        self.calendar_file[year] = work_calendar
        super().dump_data(
            data_path=self.calendar_path,
            base_to_dump=self.calendar_file,
            user=self.user,
        )
        print(f"Рабочий календарь {year} создан.")
        print(work_calendar)
        input('\n[ENTER] - выйти.')

    def show_year_shifts(self):
        """Show shift calendar by year."""
        print('[нажмите ENTER]'
              "\nВыберете год:")
        year = super().choise_from_list(self.calendar_file, none_option=True)
        if year:
            super().clear_screen()
            print(self.calendar_file[year])
            input('\n[ENTER] - выйти.')

    def give_current_brigade(self, cur_date: List[int]) -> str:
        """Return current brigade."""
        shift_day = self.calendar_file[cur_date[0]].br_cal[cur_date[1]-1][0]
        if cur_date[2] <= shift_day:
            cur_brig = 'Бригада 1'
        else:
            cur_brig = 'Бригада 2'
        return cur_brig

    def give_current_itr(self, cur_date: List[int]) -> str:
        """Return current ITR."""
        shift_days = self.calendar_file[cur_date[0]].itr_cal[cur_date[1]-1]
        if cur_date[2] <= shift_days[0] or cur_date[2] >= shift_days[1]:
            cur_itr = 'Смена 1'
        else:
            cur_itr = 'Смена 2'
        return cur_itr

    def give_current_month_shifts(self, cur_date: List[int],
                                  cal_format='text') -> str:
        """Return current month shifts."""
        shifts_cal = (self.calendar_file[cur_date[0]]
                      .give_month_shifts(cur_date[1]-1, cal_format))
        return shifts_cal
