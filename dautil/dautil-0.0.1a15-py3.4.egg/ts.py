import pandas as pd
import calendar


def groupby_yday(df):
    return df.groupby(lambda d: d.timetuple().tm_yday)


def groupby_month(df):
    return df.groupby(df.index.month)


def groupby_year_month(df):
    return pd.groupby(df, by=[df.index.year, df.index.month])


def short_month(i, zero_based=False):
    j = i

    if zero_based:
        if i < 0 or i > 11:
            raise AssertionError("Out of range " + i)

        j = i + 1

    return calendar.month_abbr[j]


def short_months():
    return [short_month(i) for i in range(12)]


def month_index(month, zero_based=False):
    for i, m in enumerate(short_months()):
        if m == month:
            index = i

            if not zero_based:
                index += 1

            return i
