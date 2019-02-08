# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
#  This code is licensed under MIT license (see license.txt for details)

import math
import itertools
import datetime
import pandas as pd
from dativa.tools.pandas import string_to_datetime, datetime_to_string


class ColumnStats:
    """A class that describes the stats for a column"""
    minimum = None
    maximum = None
    references = None

    def __init__(self, analyser, row, clean_threshold, outlier_threshold):
        self.analyser = analyser
        self.name = str(row["column"])
        self.sample_records = row["sample_records"]
        self.sample_blank = row["sample_blank"]
        self.sample_number = row["sample_number"]
        self.sample_string = row["sample_string"]
        self.sample_dates = row["sample_dates"]
        self.total_records = row["total_records"]
        self.total_unique = row["total_unique"]
        self.string_min_length = row["string_min_length"]
        self.string_max_length = row["string_max_length"]
        self.string_3std_min_length = row["string_3std_min_length"]
        self.string_3std_max_length = row["string_3std_max_length"]
        self.number_minimum = row["number_minimum"]
        self.number_maximum = row["number_maximum"]
        self.number_3std_minimum = row["number_3std_minimum"]
        self.number_3std_maximum = row["number_3std_maximum"]
        self.date_format = row["date_format"]
        self.date_minimum = row["date_minimum"]
        self.date_maximum = row["date_maximum"]
        self.date_3std_minimum = row["date_3std_minimum"]
        self.date_3std_maximum = row["date_3std_maximum"]
        self.decimal_places = row["decimal_places"]
        self.mode = row["mode"]

        # derived numbers
        self.sample_non_blanks = self.sample_records - self.sample_blank
        self.sample_percent_blank = self.sample_blank / self.sample_records
        if self.sample_non_blanks > 0:
            self.percent_string = self.sample_string / self.sample_non_blanks
            self.percent_date = self.sample_dates / self.sample_non_blanks
            self.percent_number = self.sample_number / self.sample_non_blanks
        else:
            self.percent_string = 0
            self.percent_date = 0
            self.percent_number = 0

        self.clean_threshold = clean_threshold
        self.outlier_threshold = outlier_threshold

    def _round(self, i, round_up):
        if i < 0:
            return - self._round(-i, not round_up)
        elif i < 1:
            return 0

        power_of_ten = int(math.pow(10, round(math.log10(i))))

        if power_of_ten == 1:
            if round_up:
                return 10
            else:
                return 1

        integer = int(i / power_of_ten)
        remainder = (i / power_of_ten) - integer

        if round_up and remainder > 0:
            return (integer + 1) * power_of_ten
        else:
            return integer * power_of_ten

    def _round_down(self, i):
        return self._round(i, False)

    def _round_up(self, i):
        return self._round(i, True)

    @staticmethod
    def _round_dates(min_val, max_val):
        if (max_val - min_val) > datetime.timedelta(days=31):
            return min_val.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0), max_val.replace(month=12,
                                                                                                               day=31,
                                                                                                               hour=23,
                                                                                                               minute=59,
                                                                                                               second=59,
                                                                                                               microsecond=999999)
        elif (max_val - min_val) > datetime.timedelta(days=1):
            return min_val.replace(day=1, hour=0, minute=0, second=0, microsecond=0), max_val.replace(
                year=max_val.year + int(max_val.month / 12), month=(max_val.month + 1) % 12, day=1, hour=0, minute=0,
                second=0, microsecond=0) - datetime.timedelta(microseconds=1)
        elif (max_val - min_val) > datetime.timedelta(hours=1):
            return min_val.replace(hour=0, minute=0, second=0, microsecond=0), max_val.replace(hour=23, minute=59,
                                                                                               second=59,
                                                                                               microsecond=999999)
        else:
            return min_val.replace(minute=0, second=0, microsecond=0), max_val.replace(minute=59, second=59,
                                                                                       microsecond=999999)

    def _guess_min(self, minimum, min_3std):
        if min_3std * self.outlier_threshold < minimum:
            return min_3std
        else:
            return minimum

    def _guess_max(self, maximum, max_3std):
        if max_3std * self.outlier_threshold > maximum:
            return max_3std
        else:
            return maximum

    @property
    def type(self):
        if self.percent_number > self.clean_threshold:
            return "number"
        elif self.percent_date > self.clean_threshold and self.date_format != '':
            return "date"
        else:
            return "string"

    @property
    def is_unique(self):
        return self.total_unique / self.total_records > self.clean_threshold

    def _get_min_max(self):
        if self.type == "number":
            min_val = self._guess_min(self.number_minimum, self.number_3std_minimum)
            max_val = self._guess_max(self.number_maximum, self.number_3std_maximum)

            return self._round_down(min_val), self._round_up(max_val)

        if self.type == "date":
            min_diff = self.date_3std_minimum - self.date_minimum
            max_diff = self.date_maximum - self.date_3std_maximum
            std3_diff = self.date_3std_maximum - self.date_3std_minimum

            if min_diff > std3_diff * self.outlier_threshold:
                min_val = self.date_3std_minimum
            else:
                min_val = self.date_minimum

            if max_diff > std3_diff * self.outlier_threshold:
                max_val = self.date_3std_maximum
            else:
                max_val = self.date_maximum

            return self._round_dates(min_val, max_val)
        else:
            return (self._round_down(self._guess_min(self.string_min_length, self.string_3std_min_length)),
                    self._round_up(self._guess_max(self.string_max_length, self.string_3std_max_length)))

    def _check_min_max(self):
        if self.minimum is None or self.maximum is None:
            self.minimum, self.maximum = self._get_min_max()

    @property
    def min(self):
        self._check_min_max()
        return self.minimum

    @property
    def max(self):
        self._check_min_max()
        return self.maximum

    @property
    def has_blanks(self):
        return self.sample_percent_blank > (1 - self.clean_threshold)

    @property
    def fallback_mode(self):
        if self.type == "date":
            return "quarantine"
        elif self.type == "number":
            return "quarantine"
        elif self.type == "string":
            if self.number_references == 0:
                return "default"
            else:
                if self.number_references == self.total_unique:
                    return "quarantine"
                else:
                    return "closest"

    def _get_references(self):
        references = []
        if self.type == "string":
            # calculate reference rules
            maximum_records = self.total_records / self.analyser.min_occurences

            references = self.analyser.get_reference_list(self, maximum_records)

        return references

    def _check_references(self):
        if self.references is None:
            self.references = self._get_references()

    @property
    def reference_list(self):
        self._check_references()
        return self.references

    @property
    def number_references(self):
        self._check_references()
        return len(self.references)

    @property
    def default_value(self):
        if self.has_blanks or self.mode is None:
            return ""
        else:
            return self.mode


class DataFrameAnalyzer:
    """A class that contains functions to to analyse a passed DataFrame"""

    date_formats = ["%A, %B %d, %Y",
                    "%A, %B %d, %Y %I:%M:%S %p",
                    "%a, %d %b %Y %H:%M:%S %Z",
                    "%B, %Y",
                    "%d-%m-%Y %H:%M:%S"
                    "%d/%b/%Y:%H:%M:%S %z",
                    "%d/%m/%Y %H:%M:%S",
                    "%d/%m/%Y %H:%M",
                    "%d/%m/%Y",
                    "%H:%M:%S",
                    "%H:%M",
                    "%I:%M:%S %p",
                    "%I:%M:%S%p",
                    "%I:%M %p",
                    "%I:%M%p",
                    "%m/%d/%Y %I:%M:%S %p",
                    "%m/%d/%Y",
                    "%s",
                    "%Y%m%d %H%M%S",
                    "%Y%m%d %H:%M:%S",
                    "%Y%m%dT%H:%M:%S",
                    "%Y%m%dT%I:%M:%S %p",
                    "%Y%m%dT%H%M%S",
                    "%Y%m%dt%I%M%S %p",
                    "%Y-%m-%d %H:%M:%SZ",
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S.000Z",
                    "%Y-%m-%dT%H:%M:%S.%fZ",
                    "%Y-%m-%dT%H:%M:%S.000",
                    "%Y-%m-%dT%H:%M:%S.%f",
                    "%Y-%m-%dT%I:%M:%S %p",
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y/%m/%d %H:%M:%S",
                    "%Y/%m/%d",
                    "%Y:%m:%d %H:%M:%S"
                    ]

    def __init__(self,
                 df,
                 large_sample_size=5000,
                 small_sample_size=100,
                 clean_threshold=0.95,
                 outlier_threshold=2,
                 min_occurences=5):
        """Initiate a DataFrameAnalyser class, takes
        - df: the DataFrame to be analysed
        - large_sample_size: the maximum sample size to be taken for type-specific analysis
        - small_sample_size: the smaller sample size for inferring date format, decimal places
        """
        for d in df.dtypes:
            if d != object:
                raise Exception("DataFrame can only contain string columns, found type {0}".format(d))

        self.df = df
        self.large_sample_size = large_sample_size
        if self.large_sample_size > self.df.shape[0]:
            self.large_sample_size = self.df.shape[0]
        self.clean_threshold = clean_threshold
        self.outlier_threshold = outlier_threshold
        self.sample = self.df.sample(self.large_sample_size)
        self.min_occurences = min_occurences
        if small_sample_size > self.large_sample_size:
            self.small_sample_size = self.large_sample_size
        else:
            self.small_sample_size = small_sample_size
        self.small_sample = self.sample.sample(self.small_sample_size)
        self.columns = []

        for i, r in self._get_df_stats().iterrows():
            self.columns.append(ColumnStats(self, r, clean_threshold, outlier_threshold))

    @staticmethod
    def _is_number(s):
        try:
            float(s)
        except ValueError:
            return False
        else:
            return True

    def _get_number_string_blank(self, s):
        """Return the type of the passed string as either:
            b - blank
            n - number
            d - date
            s - string
        """
        if s == '' or s == 'nan':
            return 'b'
        if self._is_number(s):
            return "n"
        return "s"

    @staticmethod
    def _count(column, df, value):
        """return the number of records in the DataFrame's column with a specific value"""
        return df.loc[df[column] == value, column].count()

    @staticmethod
    def _std3_min_max(series):
        """returns the minimum and maximum values of the series within 3 standard deviations of the mean"""
        if series.shape[0] > 0:
            if series.shape[0] > 1:
                series = series[~((series - series.mean()).abs() > 3 * series.std())]
            return series.min(), series.max()
        return pd.Series(0), pd.Series(0)

    ##################
    # STRING STATISTICS
    ##################

    @staticmethod
    def _strlen(df, types, column):
        """returns the length of each row"""
        lengths = df.loc[types[column] != 'b', column].str.len()
        if lengths.shape[0] == 0:
            return pd.Series(0)
        else:
            return lengths

    def _get_string_stats(self, stats_df, types, df):
        """calculates summary statistics on all string rows"""
        minimum = stats_df["column"].map(lambda c: self._strlen(df, types, c).min())
        maximum = stats_df["column"].map(lambda c: self._strlen(df, types, c).max())
        min_3std, max_3std = zip(*stats_df["column"].map(lambda c: self._std3_min_max(self._strlen(df, types, c))))

        return minimum, maximum, min_3std, max_3std

    ##################
    # NUMBER STATISTICS
    ##################

    @staticmethod
    def _get_decimal_places(c):
        """returns the the number of decimal places in the string"""
        try:
            s = str(c)
            return len(s) - s.index('.') - 1
        except ValueError:
            return 0

    def _get_dp_frequency(self, column):
        """function to calculate the required decimal places to get the threshold fraction
        of the records included"""
        numbers = self.small_sample.loc[self.small_sample[column].map(lambda s: self._is_number(str(s))), column]
        if len(numbers) > 0:
            dp = numbers.map(lambda n: self._get_decimal_places(n))
            return int(dp.max())
        return 0

    @staticmethod
    def _number(df, types, column):
        """returns the numeric value of each row"""
        return pd.to_numeric(df.loc[types[column] == 'n', column], errors="coerce")

    def _get_number_stats(self, stats_df, types, df):
        # basic stats
        minimum = stats_df["column"].map(lambda c: self._number(df, types, c).min())
        maximum = stats_df["column"].map(lambda c: self._number(df, types, c).max())
        min_3std, max_3std = zip(*stats_df["column"].map(lambda c: self._std3_min_max(self._number(df, types, c))))
        return (minimum,
                maximum,
                min_3std,
                max_3std)

    ##################
    # DATE STATISTICS
    ##################

    def _get_date_format(self, df, types, column):
        """get the date format string"""
        date_format = ""
        if len(df.loc[types[column] == 'd', column]) > 0:
            for f in self.date_formats:
                try:
                    timestamp = string_to_datetime(
                        df.loc[df.loc[types[column] == 'd', column].notnull().index, column].iloc[0], format=f)
                    string = df.loc[df.loc[types[column] == 'd', column].notnull().index, column].iloc[0]
                    if string == datetime_to_string(timestamp, f):
                        date_format = f
                        break
                except ValueError:
                    pass
        return date_format

    @staticmethod
    def _date(df, types, column, f):
        """return a date"""
        return string_to_datetime(df.loc[types[column] == 'd', column], f, errors="coerce")

    @staticmethod
    def _std3_date_min_max(series):
        """returns the minimum and maximum values of a series of dates within 3 standard deviations of the mean"""
        if series.shape[0] > 0:
            ts = series[series.notnull()].astype('int64')
            if ts.shape[0] > 1:
                ts = ts[~((ts - ts.mean()).abs() > 3 * ts.std())]
            return pd.to_datetime(ts.min(), unit='ns'), pd.to_datetime(ts.max(), unit='ns')
        return pd.np.nan, pd.np.nan

    def _get_date_stats(self, stats_df, types, df):
        """calculate the statistics for date columns"""
        minimum = stats_df[["column", "date_format"]].apply(lambda row: self._date(df, types, row[0], row[1]).min(),
                                                            axis=1)
        maximum = stats_df[["column", "date_format"]].apply(lambda row: self._date(df, types, row[0], row[1]).max(),
                                                            axis=1)
        min_3std, max_3std = zip(*stats_df[["column", "date_format"]].apply(
            lambda row: self._std3_date_min_max(self._date(df, types, row[0], row[1])), axis=1))

        return (minimum,
                maximum,
                min_3std,
                max_3std)

    def _get_mode(self, c):
        m = self.df.loc[self.df[c] != "", c].mode()
        if m.size == 0:
            return None
        else:
            return m[0]

    def _get_df_stats(self):
        """Returns a DataFrame that contains summary statistics for each
        column in the passed DataFrame. Some statistics are time intensive to calculate,
        so a sample is used based on the parameter large_sample_size"""

        # setup the DataFrame...
        stats_df = pd.DataFrame()

        # calculate the type of each field in the sample...
        types = self.sample.applymap(lambda x: self._get_number_string_blank(str(x)))

        # check the date formats
        types[self.sample[types == 'n'].applymap(lambda c: float(c) > 631152000 and float(c) < 4102444800)] = 'd'
        for c in types.columns:
            strings = self.small_sample.loc[types[c] == 's', c]
            if strings.shape[0] > 0:
                for f in self.date_formats:
                    try:
                        timestamp = string_to_datetime(strings, format=f, errors="raise").iloc[0]
                        if datetime_to_string(timestamp, f) == strings.iloc[0]:
                            types.loc[(types == 's').index, c] = 'd'
                            break
                    except ValueError:
                        pass

        # add the basic summary statistics...
        stats_df["column"] = types.columns
        stats_df["sample_records"] = types.shape[0]
        stats_df["sample_blank"] = stats_df["column"].map(lambda c: self._count(c, types, "b"))
        stats_df["sample_number"] = stats_df["column"].map(lambda c: self._count(c, types, "n"))
        stats_df["sample_string"] = stats_df["column"].map(lambda c: self._count(c, types, "s"))
        stats_df["sample_dates"] = stats_df["column"].map(lambda c: self._count(c, types, "d"))
        stats_df["total_records"] = self.df.shape[0]

        # add the unique statistics...
        stats_df["total_unique"] = stats_df["column"].map(lambda c: self.df[c].unique().shape[0])

        # get the most common value...
        stats_df["mode"] = stats_df["column"].map(lambda c: self._get_mode(c))

        # get the string stats...
        (stats_df["string_min_length"],
         stats_df["string_max_length"],
         stats_df["string_3std_min_length"],
         stats_df["string_3std_max_length"]) = self._get_string_stats(stats_df, types, self.sample)

        # get the date stats...
        stats_df["date_format"] = stats_df["column"].map(lambda c: self._get_date_format(self.small_sample, types, c))
        (stats_df["date_minimum"],
         stats_df["date_maximum"],
         stats_df["date_3std_minimum"],
         stats_df["date_3std_maximum"]) = self._get_date_stats(stats_df, types, self.sample)

        # get the number stats...
        (stats_df["number_minimum"],
         stats_df["number_maximum"],
         stats_df["number_3std_minimum"],
         stats_df["number_3std_maximum"]) = self._get_number_stats(stats_df, types, self.sample)

        stats_df["decimal_places"] = stats_df["column"].map(lambda c: self._get_dp_frequency(c))

        return stats_df

    def get_reference_list(self,
                           column,
                           max_records):
        """function to calculate the a reference list"""
        strings = self.df.loc[self.df[column.name].notnull().index, column.name]
        frequency = strings.value_counts()
        normalised_frequency = frequency[frequency >= self.min_occurences]
        number_normalised = normalised_frequency.shape[0]
        if (normalised_frequency.sum() > self.clean_threshold * frequency.sum() and
                number_normalised <= max_records):
            return normalised_frequency.index
        else:
            return []

    @staticmethod
    def _get_column_combinations(columns, max_cols):
        if len(columns) - 1 < max_cols:
            max_cols = len(columns) - 1
        for l in range(1, max_cols):
            for combination in itertools.combinations(columns, l):
                yield combination

    def get_unique_columns(self, threshold, max_cols):
        """This function searches for multiple column unique keys"""
        threshold_rows = self.sample.shape[0] * (1 - threshold)
        columns = self.sample.columns.values.tolist()
        for cols in self._get_column_combinations(columns, max_cols):
            number_duplicated = self.sample[self.sample.duplicated(subset=cols)].shape[0]
            if number_duplicated < threshold_rows:
                return list(cols)
        return []
