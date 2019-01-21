# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
#  This code is licensed under MIT license (see license.txt for details)

import pandas as pd
from dativa.tools.pandas import get_column_name
from .report import DefaultReportWriter


class FallbackType:
    """
    Specifies how to handle data that is not matched
    """

    USE_DEFAULT_VALUE = "use_default"
    USE_INVALID_DATA = "do_not_replace"
    REMOVE_ENTRY = "remove_record"

    def pretty(self):
        if self == FallbackType.USE_DEFAULT_VALUE:
            return "Replaced with default value"
        elif self == FallbackType.USE_INVALID_DATA:
            return "No changes made"
        elif self == FallbackType.REMOVE_ENTRY:
            return "Data quarantined"


class DateRangeType:
    """
    Specifies how data ranges should be checked
    """
    NONE = "none"
    FIXED = "fixed"
    ROLLING = "rolling"


class UniqueFieldsType:
    """
    A specific type of rule for comparing data using a duplication rule
    """

    CHECK_THIS_COLUMN_ONLY = "check_this_column_only"
    CHECK_OTHER_COLUMNS_ONLY = "check_other_columns"
    CHECK_ALL_COLUMNS = "check_all_columns"


class SessionOverlapsType:
    """
    Specifies how session overlaps should be handled
    """

    IGNORE = "ignore"
    TRUNCATE_START = "truncate_start"
    TRUNCATE_END = "truncate_end"


class SessionGapsType:
    """
    Specifies how session gaps should be handled
    """

    IGNORE = "ignore"
    EXTEND_START = "extend_start"
    EXTEND_END = "extend_end"
    INSERT_NEW = "insert_new"


class HistoryType:
    """
    Specified different types of category of error
    that can be logged to a history object
    """

    IGNORED = 'ignored'
    REPLACED = 'replaced'
    REMOVED = 'quarantined'
    MODIFIED = 'modified'
    INSERTED = 'inserted'


"""
A set of error classes raised by the FileProcessing Modules
"""


class ScrubberError(Exception):
    def __init__(self, message="File Processing Error"):
        self.message = message


class ScrubberTooManyRecordsError(Exception):
    def __init__(self, message="Too Many Records"):
        self.message = message


class ScrubberValidationError(Exception):
    def __init__(self, message="Invalid configuration"):
        self.message = message


class DefaultProfile():
    maximum_records = 2000000
    maximum_records_closest_matches = 5000
    lookalike_number_records = 5
    maximum_records_lookalike = 5000
    maximum_file_records_lookalike = 500000


class BaseAddIn:

    def __init__(self, validator):
        self.validator = validator
        self.report_writer = validator.report_writer


class BaseValidator:
    """
    The base model for Validators that are run.

    Validators must have the following:
    rule_type: a string name
    fields: a dictionary of fields, including default values and validation functions
    run(df, column=None): a function to run the validator in-situe on the passed DataFrame

    Parameters
    ----------
    params: a dict of parameters for the validator
    report_writer: a report writer class for logging
    df_dict: a dictionary of DataFrame referenced in the params function
    """
    rule_type = None
    fields = {}
    reference_list = None

    def _append_addin_fields(self, addins):
        for AddIn in addins:
            for field in AddIn.fields:
                self.fields[field] = AddIn.fields[field]

    def __init__(self, params=None, report_writer=None, df_dict=None, profile=None):

        # add any fields from the addins
        addins = []
        if hasattr(self, "pre_execution"):
            self._append_addin_fields(self.pre_execution)
            addins = addins + self.pre_execution

        if hasattr(self, "post_execution"):
            self._append_addin_fields(self.post_execution)
            addins = addins + self.post_execution

        if params is not None:
            # check for any parameters that are not in the fields...
            for param in params:
                if param not in self.fields:
                    raise ScrubberValidationError("The param {field} is not valid for {rule_type} rules".format(
                        field=param, rule_type=self.rule_type))

            # check for mandatory parameters
            for field in self.fields:
                if field in params:
                    self._validate(field, params[field])
                    setattr(self, field, params[field])
                elif self.fields[field]["default"] is None:
                    raise ScrubberValidationError("The param {field} must be set in {rule_type} rules".format(
                        field=field, rule_type=self.rule_type))
                else:
                    setattr(self, field, self.fields[field]["default"])

            # set up fixed variable
            if report_writer is None:
                self.report_writer = DefaultReportWriter()
            else:
                self.report_writer = report_writer
            if profile is None:
                self.profile = DefaultProfile()
            else:
                self.profile = profile
            if df_dict is None or type(df_dict) is dict:
                self.df_dict = df_dict
            else:
                raise ScrubberValidationError(
                    "Passed df_dict is not a python dict, type is {0}".format(type(df_dict)))

            # run any cross validation
            if hasattr(self, "cross_validation"):
                self.cross_validation()
            for AddIn in addins:
                add_in = AddIn(self)
                if hasattr(add_in, "cross_validation"):
                    add_in.cross_validation()

    def _validate(self, field, value):
        """
        Runs the validation function for a field in the validator
        """
        try:
            if self.fields[field]["validator"](value) is True:
                return
        except:  # noqa
            pass

        raise ScrubberValidationError("'{value}' is not valid for {param} in a {type} rule".format(
            param=field, value=value, type=self.rule_type))

    def get_df(self, name):
        """
        Returns a named DataFrame from within the df_dict dictionary passed
        when the class was instantiated
        """
        return pd.DataFrame(self.df_dict[name]).copy()

    def run_all(self, df, column=None):

        if column is not None and not self.fields.get('skip_blanks'):
            try:
                get_column_name(df, column)
            except KeyError as e:

                self.report_writer.log_history(
                    self.rule_type,
                    column,
                    df,
                    HistoryType.REMOVED,
                    "File did not contain required column")
                df[column] = None
                df.dropna(subset=[column], inplace=True)  # we already checked that this column does not exist
                df.drop(columns=[column], inplace=True)
                return  # goto: getout

        if hasattr(self, "pre_execution"):
            for AddIn in self.pre_execution:
                add_in = AddIn(self)
                add_in.run(df, get_column_name(df, column))

        if column is None:
            if hasattr(self, "run"):
                self.run(df)
        else:
            if hasattr(self, "run"):
                self.run(df, column)

        if hasattr(self, "post_execution"):
            for AddIn in self.post_execution:
                add_in = AddIn(self)
                add_in.run(df, df.columns[-1], get_column_name(df, column))
