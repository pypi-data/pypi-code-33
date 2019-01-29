# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
#  This code is licensed under MIT license (see license.txt for details)

import io
import re
import datetime
import pandas as pd
from pandas.api.types import is_numeric_dtype
from dativa.tools.pandas import get_column_name, get_unique_column_name, string_to_datetime, datetime_to_string, \
    is_numeric
from .base import BaseValidator, DateRangeType, HistoryType, SessionGapsType, SessionOverlapsType, ScrubberError, \
    ScrubberValidationError
from .fallback_addins import BestMatchesAddIn, FallbackAddIn, LookalikeAddIn, SkipBlankAddIn
from .anonymization import HashingAddIn, EncryptionAddIn, DecryptionAddIn


# noinspection PyUnresolvedReferences
class StringValidator(BaseValidator):
    """
    The string validator validates string columns in DataFrames
    """

    rule_type = "String"

    fields = {'minimum_length': {"default": None, "validator": lambda x: (0 <= x < 1e6)},
              'maximum_length': {"default": None, "validator": lambda x: (0 <= x < 1e6)},
              'regex': {"default": ".*", "validator": lambda x: re.compile(x, re.UNICODE) is not None},
              'is_unique': {"default": False, "validator": lambda x: x in [True, False]}}

    pre_execution = [DecryptionAddIn]
    post_execution = [SkipBlankAddIn, BestMatchesAddIn, LookalikeAddIn, FallbackAddIn, HashingAddIn,
                      EncryptionAddIn]

    def cross_validation(self):
        """
        Provides cross-validation on the fields passed to the string validator
        """
        if self.minimum_length > self.maximum_length:
            raise ScrubberValidationError(
                "minimum length cannot be greater than maximum length but {0} > {1}".format(self.minimum_length,
                                                                                            self.maximum_length))

    def _check_length(self, string):
        """
        Check that a string is within the defined length
        """
        if self.minimum_length <= len(string) <= self.maximum_length:
            return string
        else:
            return None

    def _run_string(self, string, regex):
        """
        Check the the string is valid
        """

        if pd.isnull(string):
            string = ""

        if isinstance(string, str):
            match = regex.match(string)
            if match:
                return self._check_length(string)
            else:
                return None
        else:
            return self._run_string(str(string), regex)

    def _get_regex(self):
        """
        compile a regex from the fields
        """
        if self.regex == '':
            return re.compile('.*', re.UNICODE)

        return re.compile(self.regex, re.UNICODE)

    def run(self, df, column):
        """
        Run the string validator against the passed column of the DataFrame
        """

        dirty_col = get_column_name(df, column)
        clean_col = get_unique_column_name(df, dirty_col)

        # create the regex
        regex = self._get_regex()

        if self.is_unique:
            dupes = df[df.duplicated(subset=dirty_col, keep='first')]
            if dupes.shape[0] > 0:
                self.report_writer.log_history(
                    self.rule_type,
                    dirty_col,
                    df[df.duplicated(subset=dirty_col, keep='first')],
                    HistoryType.REMOVED,
                    "Removed duplicates")
                df.drop_duplicates(
                    subset=dirty_col, keep='first', inplace=True)

        # add a new column for the clean data
        df[clean_col] = df[dirty_col].map(
            lambda word: self._run_string(word, regex))

        # set up the reference list for best matches...
        self.reference_list = pd.Series(df[clean_col].dropna().unique())


# noinspection PyUnresolvedReferences
class NumberValidator(BaseValidator):
    """
    The number validator runs validation against number fields in the data
    """

    rule_type = "Number"

    fields = {'decimal_places': {"default": None, "validator": lambda x: (0 <= x < 100)},
              'minimum_value': {"default": None, "validator": lambda x: (-1e24 <= x < 1e24)},
              'maximum_value': {"default": None, "validator": lambda x: (-1e24 <= x < 1e24)},
              'fix_decimal_places': {"default": None, "validator": lambda x: x in [True, False]},
              'is_unique': {"default": False, "validator": lambda x: x in [True, False]}}

    pre_execution = []
    post_execution = [SkipBlankAddIn, BestMatchesAddIn, LookalikeAddIn, FallbackAddIn]

    def cross_validation(self):
        """
        Provides cross-validation on the fields passed to the string validator
        """
        if self.minimum_value > self.maximum_value:
            raise ScrubberValidationError(
                "minimum value cannot be greater than maximum value but {0} > {1}".format(self.minimum_value,
                                                                                          self.maximum_value))

    def _get_regex(self):
        """
        Get the regex to validate for the number of decimal places
        """

        if self.decimal_places == 0:
            regex_string = "^\\d+$"
        else:
            regex_string = "^-?\\d+\\." + "\\d" * self.decimal_places + "$"
        return re.compile(regex_string, re.UNICODE)

    @staticmethod
    def _force_format_string(number_string, format_string):
        """
        Forces the number to the specified format string
        """
        return format_string.format(float(number_string))

    def _validate_number(self, string, regex, format_string):
        """
        Run number validation
        """

        # first check that it is in range
        try:
            number = float(string)
            if not self.minimum_value <= number <= self.maximum_value:
                return None
        except ValueError:
            return None

        # now check the decimal places...
        if self.fix_decimal_places:
            # attempt to fix dirty data with correct decimcal places
            return self._force_format_string(string, format_string)
        else:
            match = regex.match(string)
            if match:
                return string
            else:
                return None

    def run(self, df, column):
        """
        Run the number validator against the passed column of the DataFrame
        """

        dirty_col = get_column_name(df, column)
        clean_col = get_unique_column_name(df, dirty_col)
        write_report_dp = None

        # check range then (optionally) fix decimal places
        if is_numeric_dtype(df[dirty_col]):
            # we are validating a number
            df[clean_col] = df.loc[
                (self.minimum_value <= df[dirty_col]) & (df[dirty_col] <= self.maximum_value), dirty_col].round(
                self.decimal_places)

            if not self.fix_decimal_places:
                df.loc[df[clean_col] != df[dirty_col], clean_col] = None
            elif self.fix_decimal_places:

                # all entries which are rounded (regardless of if they matched already)
                write_report_dp = df.loc[
                    (df[clean_col] == df[dirty_col].round(self.decimal_places)), [dirty_col, clean_col]]
        else:
            # we are validating a string
            regex = self._get_regex()
            format_string = "{{0:.{0}f}}".format(self.decimal_places)

            df[clean_col] = df[dirty_col].map(lambda word: self._validate_number(word, regex, format_string))

            if self.fix_decimal_places and (df[df[clean_col] != df[dirty_col]].dropna().shape[0] > 0):
                write_report_dp = df[df[clean_col] != df[dirty_col]].dropna()

        # write report if it has changed the number of decimal places
        if write_report_dp is not None:
            self.report_writer.log_history(
                self.rule_type,
                dirty_col,
                write_report_dp,
                HistoryType.MODIFIED,
                "Automatically fixed to {0} decimal places".format(self.decimal_places))

        # remove duplicated entries
        if self.is_unique:
            dupes = df[df.duplicated(subset=clean_col, keep='first')]
            if dupes.shape[0] > 0:
                self.report_writer.log_history(
                    self.rule_type,
                    clean_col,
                    dupes,
                    HistoryType.REMOVED,
                    "Removed duplicates")
                df.drop_duplicates(
                    subset=clean_col, keep='first', inplace=True)

        # set up the reference list for best matches...
        self.reference_list = pd.Series(df[clean_col].dropna().unique())


# noinspection PyUnresolvedReferences
class DateValidator(BaseValidator):
    """
    Runs data validation
    """

    rule_type = "Date"

    fields = {'date_format': {"default": None,
                              "validator": lambda x: datetime_to_string(datetime.datetime.now(), x) is not None},
              'range_check': {"default": DateRangeType.NONE,
                              "validator": lambda x: x in [DateRangeType.NONE, DateRangeType.FIXED,
                                                           DateRangeType.ROLLING]},
              'range_minimum': {"default": "none", "validator": lambda x: True},
              'range_maximum': {"default": "none", "validator": lambda x: True},
              'is_unique': {"default": False, "validator": lambda x: x in [True, False]}}

    pre_execution = []
    post_execution = [SkipBlankAddIn, BestMatchesAddIn, LookalikeAddIn, FallbackAddIn]

    def cross_validation(self):
        """
        Provides cross-validation on the fields passed to the date validator
        """
        if self.range_check != DateRangeType.NONE:
            if self.range_minimum == "none":
                raise ScrubberValidationError(
                    "range_minimum must be set if range_check is not set to {0}".format(DateRangeType.NONE))
            if self.range_maximum == "none":
                raise ScrubberValidationError(
                    "range_maximum must be set if range_check is not set to {0}".format(DateRangeType.NONE))
            if self.range_check == DateRangeType.ROLLING:
                if not is_numeric(self.range_minimum):
                    raise ScrubberValidationError(
                        "range_minimum must be a number if range_type={0}".format(DateRangeType.ROLLING))
                if not is_numeric(self.range_maximum):
                    raise ScrubberValidationError(
                        "range_minimum must be a number if range_type={0}".format(DateRangeType.ROLLING))
            else:
                if string_to_datetime(self.range_minimum, self.date_format, errors="coerce") is pd.NaT:
                    raise ScrubberValidationError(
                        "range_minimum does not match the data format {0}".format(self.date_format))
                if string_to_datetime(self.range_maximum, self.date_format, errors="coerce") is pd.NaT:
                    raise ScrubberValidationError(
                        "range_maximum does not match the data format {0}".format(self.date_format))
            if self.range_minimum > self.range_maximum:
                raise ScrubberValidationError(
                    "range_minimum cannot be greater than range_maximum but {0} > {1}".format(self.range_minimum,
                                                                                              self.range_maximum))

    def run(self, df, column):
        """
        Run the date validator against the passed column of the DataFrame
        """
        dirty_col = get_column_name(df, column)
        clean_col = get_unique_column_name(df, dirty_col)
        date_col = get_unique_column_name(df, "zxc34324uih")

        if self.is_unique:
            dupes = df[df.duplicated(subset=dirty_col, keep='first')]
            if dupes.shape[0] > 0:
                self.report_writer.log_history(
                    self.rule_type,
                    dirty_col,
                    dupes,
                    HistoryType.REMOVED,
                    "Removed duplicates")
                df.drop_duplicates(
                    subset=dirty_col, keep='first', inplace=True)

        if pd.core.dtypes.common.is_datetime_or_timedelta_dtype(df[dirty_col]):
            df[date_col] = df[dirty_col]
        else:
            df[date_col] = string_to_datetime(df[dirty_col], format=self.date_format, errors='coerce')
        if self.range_check != DateRangeType.NONE:
            if self.range_check == DateRangeType.ROLLING:
                min_date = datetime.datetime.now() + datetime.timedelta(days=int(self.range_minimum))
                max_date = datetime.datetime.now() + datetime.timedelta(days=int(self.range_maximum))
            else:
                min_date = string_to_datetime(
                    self.range_minimum, self.date_format)
                max_date = string_to_datetime(
                    self.range_maximum, self.date_format)

            df.loc[df[date_col] < min_date, date_col] = pd.np.NaN
            df.loc[df[date_col] > max_date, date_col] = pd.np.NaN

        # now update the clean column...
        df.loc[df[date_col].notnull(), clean_col] = datetime_to_string(
            df[date_col], self.date_format)
        df.drop(date_col, axis=1, inplace=True)

        # set up the reference list for best matches...
        self.reference_list = pd.Series(df[clean_col].dropna().unique())


# noinspection PyUnresolvedReferences
class LookupValidator(BaseValidator):
    """
    """

    rule_type = "Lookup"

    fields = {'original_reference': {"default": None, "validator": lambda x: True},
              'reference_field': {"default": None, "validator": lambda x: True},
              'blacklist': {"default": False, "validator": lambda x: x in (True, False)}}

    pre_execution = []
    post_execution = [SkipBlankAddIn, BestMatchesAddIn, LookalikeAddIn, FallbackAddIn]

    def _get_reference_df(self):
        """
        Loads the reference data into a DataFrame
        """

        # load the initially provided data
        reference_words = self.get_df(self.original_reference)
        reference_column = get_column_name(reference_words, self.reference_field)

        # drop the other columns
        if reference_words.shape[1] > 1:
            for col in reference_words.columns:
                if col != reference_column:
                    reference_words.drop(col, axis=1, inplace=True)

        reference_words.drop_duplicates(
            subset=reference_column, keep='first', inplace=True)

        return reference_words, reference_column

    def run(self, df, column):
        """
        Run the lookup validator against the passed column of the DataFrame
        """

        reference_df, reference_column = self._get_reference_df()

        dirty_col = get_column_name(df, column)
        clean_col = get_unique_column_name(df, dirty_col)
        ref_col = reference_column

        # join the dirty DataFrame to the clean DataFrame for any exact matches
        reference_df.rename(
            columns={ref_col: clean_col}, inplace=True)
        cleaned = df.loc[:, [dirty_col]].merge(
            reference_df, left_on=dirty_col, right_on=clean_col, copy=False, how='left').set_index(df.index)

        if self.blacklist:
            # exclude any matches...
            df[clean_col] = df.loc[cleaned[clean_col].isnull(), dirty_col]

            # setup the reference list for the best matches...
            self.reference_list = pd.Series(df[clean_col].dropna().unique())
        else:
            # set any matching columns
            df[clean_col] = cleaned[clean_col]

            # use the reference dataframe as the reference list for best matches
            self.reference_list = reference_df[clean_col].copy()


# noinspection PyUnresolvedReferences
class UniqueFieldsValidator(BaseValidator):
    """
    Tests combinations of columns for uniqueness
    """

    rule_type = "Uniqueness"

    fields = {'use_last_value': {"default": False, "validator": lambda x: x in [True, False]},
              'unique_fields': {"default": None, "validator": lambda x: True}}

    pre_execution = []
    post_execution = []

    def _get_columns_from_unique(self, df, separator=","):
        """
        Get a validated list of columns based on the passed string of unique fields
        """
        unique_fields = self.unique_fields.split(separator)
        cols = df.columns.values.tolist()

        # get the unique fields...
        for field in unique_fields:
            if field not in cols:
                raise ScrubberError(
                    "The field {0} was not present in the source file".format(field))

        return unique_fields

    def _get_keep_option(self):
        """
        Returns the pandas keep option based on whether to keep the first
        or last value
        """

        if self.use_last_value is True:
            keep_option = 'last'
            return keep_option
        else:
            keep_option = 'first'
            return keep_option

    def run(self, df):
        """
        Run the automatic uniqueness validator algorithm on the passed columns of the DataFrame
        """

        keep_option = self._get_keep_option()
        unique_columns = self._get_columns_from_unique(df)

        dupes = df[df.duplicated(subset=unique_columns, keep=keep_option)]
        if dupes.shape[0] > 0:
            self.report_writer.log_history(
                self.rule_type,
                self.unique_fields,
                df[df.duplicated(subset=unique_columns, keep=keep_option)],
                HistoryType.REMOVED,
                "Removed duplicates")
            df.drop_duplicates(subset=unique_columns,
                               keep=keep_option, inplace=True)


# noinspection PyUnresolvedReferences
class SessionValidator(BaseValidator):
    """
    Runs session validation
    """

    rule_type = "Session"

    fields = {'key_field': {"default": None, "validator": lambda x: True},
              'start_field': {"default": None, "validator": lambda x: True},
              'end_field': {"default": None, "validator": lambda x: True},
              'overlaps_option': {"default": None, "validator": lambda x: x in [SessionOverlapsType.IGNORE,
                                                                                SessionOverlapsType.TRUNCATE_START,
                                                                                SessionOverlapsType.TRUNCATE_END]},
              'gaps_option': {"default": None,
                              "validator": lambda x: x in [SessionGapsType.IGNORE, SessionGapsType.EXTEND_START,
                                                           SessionGapsType.EXTEND_END, SessionGapsType.INSERT_NEW]},
              'date_format': {"default": None,
                              "validator": lambda x: datetime_to_string(datetime.datetime.now(), x) is not None},
              'allowed_gap_seconds': {"default": 0, "validator": lambda x: (0 <= x <= 3600)},
              'allowed_overlap_seconds': {"default": 0, "validator": lambda x: (0 <= x <= 3600)},
              'template_for_new': {"default": "", "validator": lambda x: True},
              'remove_zero_length': {"default": True, "validator": lambda x: True}}

    pre_execution = []
    post_execution = []

    @staticmethod
    def _string_to_df(string, columns):
        """
        Returns a DataFrame from a passed string
        """
        f = io.StringIO()
        f.write(string)
        f.seek(0)
        return pd.read_csv(f,
                           dtype=pd.np.str,
                           skipinitialspace=True,
                           encoding="UTF-8",
                           delimiter=",",
                           quotechar="\"",
                           header=None,
                           names=columns)

    def _setup_columns(self, df):
        """
        Sets up the additional columns needed in the DataFrame and the columns dictionary
        """
        cols = dict()
        cols["key"] = get_column_name(df, self.key_field)
        cols["next_key"] = get_unique_column_name(df, "next_key")
        cols["previous_key"] = get_unique_column_name(df, "previous_key")
        cols["start"] = get_unique_column_name(df, "start")
        cols["end"] = get_unique_column_name(df, "end")
        cols["next_start"] = get_unique_column_name(df, "next")
        cols["previous_end"] = get_unique_column_name(df, "previous")

        cols["original_start"] = get_column_name(df, self.start_field)
        cols["original_end"] = get_column_name(df, self.end_field)

        df[cols["start"]] = string_to_datetime(
            df[cols["original_start"]], format=self.date_format)
        df[cols["end"]] = string_to_datetime(
            df[cols["original_end"]], format=self.date_format)

        df.sort_values([cols["key"], cols["start"], cols["end"]], inplace=True)

        df[cols["next_key"]] = df[cols["key"]].shift(-1)
        df[cols["previous_key"]] = df[cols["key"]].shift(1)
        df[cols["next_start"]] = df[cols["start"]].shift(-1)
        df[cols["previous_end"]] = df[cols["end"]].shift(1)

        cols["clean_start"] = get_unique_column_name(
            df, get_column_name(df, self.start_field))
        cols["clean_end"] = get_unique_column_name(
            df, get_column_name(df, self.end_field))

        return cols

    @staticmethod
    def _clean_up_columns(df, cols):
        """
        Cleans up the additional columns in the DataFrame
        """
        df.drop(cols["next_key"], axis=1, inplace=True)
        df.drop(cols["previous_key"], axis=1, inplace=True)
        df.drop(cols["next_start"], axis=1, inplace=True)
        df.drop(cols["previous_end"], axis=1, inplace=True)
        df.drop(cols["start"], axis=1, inplace=True)
        df.drop(cols["end"], axis=1, inplace=True)
        if cols["clean_start"] in df.columns:
            df.drop(cols["clean_start"], axis=1, inplace=True)
        if cols["clean_end"] in df.columns:
            df.drop(cols["clean_end"], axis=1, inplace=True)

    def _get_rows_to_truncate(self, df, cols):
        """
        Returns a set of rows with overlapping sessions
        """
        number_seconds = pd.Timedelta(datetime.timedelta(
            seconds=self.allowed_overlap_seconds))
        if self.overlaps_option == SessionOverlapsType.TRUNCATE_START:
            return (df[cols["previous_end"]] - df[cols["start"]] > number_seconds) & (
                    df[cols["key"]] == df[cols["previous_key"]])
        else:
            return (df[cols["end"]] - df[cols["next_start"]] > number_seconds) & (
                    df[cols["key"]] == df[cols["next_key"]])

    def _run_truncation(self, df, cols):
        """
        Truncates overlapping sessions
        """
        rows = self._get_rows_to_truncate(df, cols)
        if self.overlaps_option == SessionOverlapsType.TRUNCATE_START:
            if rows[rows].shape[0] > 0:
                df.loc[rows, cols["clean_start"]] = df[cols["previous_end"]]
                self.report_writer.log_history(
                    self.rule_type,
                    cols["original_start"],
                    df.loc[rows, [cols["key"], cols["original_start"],
                                  cols["original_end"], cols["clean_start"]]],
                    HistoryType.MODIFIED,
                    "Truncated start")
        else:
            if rows[rows].shape[0] > 0:
                df.loc[rows, cols["clean_end"]] = df[cols["next_start"]]
                self.report_writer.log_history(
                    self.rule_type,
                    cols["original_end"],
                    df.loc[rows, [cols["key"], cols["original_start"],
                                  cols["original_end"], cols["clean_end"]]],
                    HistoryType.MODIFIED,
                    "Truncated end")

    def _get_rows_to_extend(self, df, cols):
        """
        Gets a list of rows with gaps
        """
        number_seconds = pd.Timedelta(
            datetime.timedelta(seconds=self.allowed_gap_seconds))
        if self.gaps_option == SessionGapsType.EXTEND_START:
            return (df[cols["start"]] - df[cols["previous_end"]] > number_seconds) & (
                    df[cols["key"]] == df[cols["previous_key"]])
        else:
            return (df[cols["next_start"]] - df[cols["end"]] > number_seconds) & (
                    df[cols["key"]] == df[cols["next_key"]])

    def _run_extension(self, df, cols):
        """
        Extends sessions to fill gaps
        """
        rows = self._get_rows_to_extend(df, cols)
        if self.gaps_option == SessionGapsType.EXTEND_START:
            if rows.shape[0] > 0:
                df.loc[rows, cols["clean_start"]] = df[cols["previous_end"]]
                self.report_writer.log_history(
                    self.rule_type,
                    cols["original_start"],
                    df.loc[rows, [cols["key"], cols["original_start"],
                                  cols["original_end"], cols["clean_start"]]],
                    HistoryType.MODIFIED,
                    "Extended start")
        else:
            if rows.shape[0] > 0:
                df.loc[rows, cols["clean_end"]] = df[cols["next_start"]]
                self.report_writer.log_history(
                    self.rule_type,
                    cols["original_end"],
                    df.loc[rows, [cols["key"], cols["original_start"],
                                  cols["original_end"], cols["clean_end"]]],
                    HistoryType.MODIFIED,
                    "Extended end")

    def _fill_gaps(self, df, cols, template_row):
        """
        Fills gaps in the session with new records
        """
        number_seconds = pd.Timedelta(
            datetime.timedelta(seconds=self.allowed_gap_seconds))
        new_rows = df[((df[cols["next_start"]] - df[cols["end"]] > number_seconds) &
                       (df[cols["key"]] == df[cols["next_key"]]))].copy()

        if new_rows.shape[0] > 0:
            new_rows[cols["original_start"]] = new_rows[cols["original_end"]]
            new_rows[cols["original_end"]] = new_rows[cols["next_start"]].apply(
                lambda x: datetime_to_string(x, self.date_format))

            for col in template_row.columns:
                if col not in [cols["original_start"], cols["original_end"], cols["key"]]:
                    new_rows[col] = template_row[col][0]

            for i, row in new_rows.iterrows():
                df.loc[len(df)] = row

            df.sort_values([cols["key"], cols["original_start"],
                            cols["original_end"]], inplace=True)

            df[cols["start"]] = string_to_datetime(
                df[cols["original_start"]], format=self.date_format)
            df[cols["end"]] = string_to_datetime(
                df[cols["original_end"]], format=self.date_format)

            self.report_writer.log_history(
                self.rule_type,
                cols["original_start"],
                new_rows[[cols["key"], cols["original_start"],
                          cols["original_end"]]],
                HistoryType.INSERTED,
                'Filled gaps')

    def _remove_zero_length_sessions(self, df, cols):
        """
        Deletes any null sessions from the dataframe
        """
        if cols["clean_start"] in df.columns:
            rows = df[df[cols["end"]] == df[cols["clean_start"]]]
        elif cols["clean_end"] in df.columns:
            rows = df[df[cols["start"]] == df[cols["clean_end"]]]
        else:
            rows = df[df[cols["start"]] == df[cols["end"]]]

        if rows.shape[0] > 0:
            self.report_writer.log_history(
                self.rule_type,
                cols["original_start"],
                rows,
                HistoryType.REMOVED,
                'Removed zero length')

            df.drop(rows.index, inplace=True)

    def run(self, df):
        """
        Run the automatic session validator algorithm on the passed column of the DataFrame
        """
        cols = self._setup_columns(df)

        if self.overlaps_option in [SessionOverlapsType.TRUNCATE_START, SessionOverlapsType.TRUNCATE_END]:
            self._run_truncation(df, cols)

        if self.gaps_option in [SessionGapsType.EXTEND_START, SessionGapsType.EXTEND_END]:
            self._run_extension(df, cols)

        if self.gaps_option == SessionGapsType.INSERT_NEW and self.template_for_new != '':
            template_row = self._string_to_df(
                self.template_for_new, df.columns)
            self._fill_gaps(df, cols, template_row)

        if self.remove_zero_length:
            self._remove_zero_length_sessions(df, cols)

        if cols["clean_start"] in df.columns:
            df.loc[df[cols["clean_start"]].notnull(), cols["original_start"]] = df.loc[df[cols["clean_start"]].notnull(
            ), cols["clean_start"]].apply(lambda x: datetime_to_string(x, self.date_format))

        if cols["clean_end"] in df.columns:
            df.loc[df[cols["clean_end"]].notnull(), cols["original_end"]] = df.loc[df[cols["clean_end"]].notnull(
            ), cols["clean_end"]].apply(lambda x: datetime_to_string(x, self.date_format))

        self._clean_up_columns(df, cols)

    def count_good_rows(self, df):
        """
        Checks for gaps and overlaps without altering the DataFrame.
        Returns the number of good rows in the DatFrame
        """

        cols = self._setup_columns(df)

        exact_matches = df[(df[cols["next_start"]] == df[cols["end"]]) & (
                df[cols["key"]] == df[cols["next_key"]])].shape[0]
        ineligible = df[(df[cols["key"]] != df[cols["next_key"]])].shape[0]

        gaps = df[(df[cols["next_start"]] > df[cols["end"]]) & (
                df[cols["key"]] == df[cols["next_key"]])].shape[0]
        overlaps = df[(df[cols["next_start"]] < df[cols["end"]]) & (
                df[cols["key"]] == df[cols["next_key"]])].shape[0]

        self._clean_up_columns(df, cols)

        number_good_rows = exact_matches
        if self.gaps_option == SessionGapsType.IGNORE:
            number_good_rows = number_good_rows + gaps
        if self.overlaps_option == SessionOverlapsType.IGNORE:
            number_good_rows = number_good_rows + overlaps

        return number_good_rows + ineligible
