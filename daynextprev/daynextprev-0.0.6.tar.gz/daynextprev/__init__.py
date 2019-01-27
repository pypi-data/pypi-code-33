# -*- coding: utf-8 -*-
import datetime

W_MONDAY = 0
W_TUESDAY = 1
W_WEDNESDAY = 2
W_THURSDAY = 3
W_FRIDAY = 4
W_SATURDAY = 5
W_SUNDAY = 6


class _reiter(object):
    def __init__(self, f):
        self.f = f

    def __iter__(self):
        return self.f()


def prev_month(y, m):
    if m == 1:
        return (y - 1, 12)
    else:
        return (y, m - 1)


def next_month(y, m):
    if m == 12:
        return (y + 1, 1)
    else:
        return (y, m + 1)


def is_less_ym(ym1, ym2):
    y1, m1 = ym1
    y2, m2 = ym2

    if y1 < y2:
        return True
    elif y1 == y2 and m1 < m2:
        return True
    else:
        return False


def months(ym_start, ym_end, include_end=True):
    if include_end:
        ym_end = next_month(*ym_end)

    def _months():
        ym = ym_start
        while is_less_ym(ym, ym_end):
            yield ym
            ym = next_month(*ym)

    return _reiter(_months)


def months_backward(ym_start, ym_end, include_end=True):
    if include_end:
        ym_end = ym_end = prev_month(*ym_end)

    def _months():
        ym = ym_start
        while is_less_ym(ym_end, ym):
            yield ym
            ym = prev_month(*ym)

    return _reiter(_months)


def is_leapyear(y):
    if y % 400 == 0:
        return True
    elif y % 100 == 0:
        return False
    elif y % 4 == 0:
        return True
    else:
        return False


def days_of_month(y, m):
    if m == 2:
        return (29 if is_leapyear(y) else 28)
    elif m in (1, 3, 5, 7, 8, 10, 12):
        return 31
    else:
        return 30


def _next_day(y, m, d):
    if d == days_of_month(y, m):
        if m == 12:
            return (y + 1, 1, 1)
        else:
            return (y, m + 1, 1)
    else:
        return (y, m, d + 1)


def dt2tuple(dt):
    return (dt.year, dt.month, dt.day)


def tuple2dt(ymd):
    return datetime.date(ymd[0], ymd[1], ymd[2])


def next_day(*args):
    if len(args) == 1 and isinstance(args[0], datetime.date):
        y, m, d = _next_day(*dt2tuple(args[0]))
        return datetime.date(y, m, d)
    else:
        return _next_day(*args)


def _prev_day(y, m, d):
    if d == 1:
        if m == 1:
            return (y - 1, 12, 31)
        else:
            bm = m - 1
            return (y, bm, days_of_month(y, bm))
    else:
        return (y, m, d - 1)


def prev_day(*args):
    if len(args) == 1 and isinstance(args[0], datetime.date):
        y, m, d = _prev_day(*dt2tuple(args[0]))
        return datetime.date(y, m, d)
    else:
        return _prev_day(*args)


def _days_dt(dt_start, dt_end, include_end=True):
    if include_end:
        dt_end = next_day(dt_end)

    def _days():
        dt = dt_start
        while dt < dt_end:
            yield dt
            dt = next_day(dt)

    return _reiter(_days)


def _days_tuple(ymd_start, ymd_end, include_end=True):
    if include_end:
        ymd_end = next_day(*ymd_end)

    def _days():
        ymd = ymd_start
        while tuple2dt(ymd) < tuple2dt(ymd_end):
            yield ymd
            ymd = next_day(*ymd)

    return _reiter(_days)


def days(d_start, d_end, include_end=True):
    if isinstance(d_start, datetime.date):
        return _days_dt(d_start, d_end, include_end)
    else:
        return _days_tuple(d_start, d_end, include_end)


def _days_backward_dt(dt_start, dt_end, include_end=True):
    if include_end:
        dt_end = prev_day(dt_end)

    def _days():
        dt = dt_start
        while dt_end < dt:
            yield dt
            dt = prev_day(dt)

    return _reiter(_days)


def _days_backward_ymd(ymd_start, ymd_end, include_end=True):
    if include_end:
        ymd_end = prev_day(*ymd_end)

    def _days():
        ymd = ymd_start
        while tuple2dt(ymd_end) < tuple2dt(ymd):
            yield ymd
            ymd = prev_day(*ymd)

    return _reiter(_days)


def days_backward(d_start, d_end, include_end=True):
    if isinstance(d_start, datetime.date):
        return _days_backward_dt(d_start, d_end, include_end)
    else:
        return _days_backward_ymd(d_start, d_end, include_end)


def this_week(d, week_start=W_MONDAY):
    while d.weekday() != week_start:
        d = prev_day(d)
    return d


def next_week(d, week_start=W_MONDAY):
    d = this_week(d, week_start=week_start)
    for _ in range(7):
        d = next_day(d)
    return d


def prev_week(d, week_start=W_MONDAY):
    d = this_week(d, week_start=week_start)
    for _ in range(7):
        d = prev_day(d)
    return d
