# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
#  This code is licensed under MIT license (see license.txt for details)

import logging
from collections import OrderedDict
import pandas as pd
from dativa.tools.pandas import get_column_name
from .base import DefaultProfile, ScrubberTooManyRecordsError, ScrubberValidationError
from .validators import NumberValidator, StringValidator, DateValidator, SessionValidator, UniqueFieldsValidator, \
    LookupValidator
from .report import DefaultReportWriter

logger = logging.getLogger("dativa.scrubber")


class Scrubber:
    """ Utility class to process jobs

    Parameters
    ----------
    report_writer : ReportWriter class that is used to write out logs from
        any jobs run using the class
    profile : User profile sets limits to the number of records that can be
        processed in any job

    Example
    -------
    fp = FileProcessor()
    df = pd.read_csv(dirty_file)

    report = fp.run(df,
                    config={"rules": [
                     {
                         "rule_type": "String",
                         "field": "Name"
                         "params": {
                             "fallback_mode": "remove_record",
                             "maximum_length": 65536,
                             "minimum_length": 1
                         },
                     }]})

    for entry in report:
        print (entry)
        print (entry.df.describe())

    See also
    --------
    DataFrame.from_records : constructor from tuples, also record arrays
    DataFrame.from_dict : from dicts of Series, arrays, or dicts
    DataFrame.from_items : from sequence of (key, value) pairs
    pandas.read_csv, pandas.read_table, pandas.read_clipboard
    """

    validators = {
        "Lookup": LookupValidator,
        "Uniqueness": UniqueFieldsValidator,
        "Session": SessionValidator,
        "Date": DateValidator,
        "Number": NumberValidator,
        "String": StringValidator
    }

    def __init__(self,
                 report_writer=None,
                 profile=None,
                 maximum_records=DefaultProfile.maximum_records,
                 maximum_records_closest_matches=DefaultProfile.maximum_records_closest_matches,
                 lookalike_number_records=DefaultProfile.lookalike_number_records,
                 maximum_records_lookalike=DefaultProfile.maximum_records_lookalike,
                 maximum_file_records_lookalike=DefaultProfile.maximum_file_records_lookalike):

        if report_writer is None:
            self._report_writer = DefaultReportWriter()
        else:
            self._report_writer = report_writer

        self.df = None

        if profile is None:
            self._profile = DefaultProfile()
            self._profile.maximum_records = maximum_records
            self._profile.maximum_records_closest_matches = maximum_records_closest_matches
            self._profile.lookalike_number_records = lookalike_number_records
            self._profile.maximum_records_lookalike = maximum_records_lookalike
            self._profile.maximum_file_records_lookalike = maximum_file_records_lookalike
        else:
            self._profile = profile

    def __del__(self):
        self.df = None

    def _extract_objects(self, obj, object_list=""):
        """"
        Generator function to yield all of the objects in a nested dict or list
        that match the passed object list
        """
        if type(obj) != str:
            for key in obj:
                if type(obj[key]) == dict or type(obj[key]) == OrderedDict:
                    yield from self._extract_objects(obj[key], object_list)
                elif type(obj[key]) == list or type(obj[key]) == tuple:
                    for index in range(0, len(obj[key])):
                        yield from self._extract_objects(obj[key][index], object_list)
                else:
                    if key in object_list:
                        yield obj[key]

    def get_files_from_config(self, config, object_list=None):
        """
        Returns all of the files specified within a config files
        """
        if object_list is None:
            object_list = ["original_reference", "token_store"]
        return self._extract_objects(config, object_list)

    def _get_validator(self, rule, df_dict):
        """
        Returns an instance of the appropriate validator class depending on the
        rule type
        """
        try:
            return self.validators[rule["rule_type"]](rule["params"], self._report_writer, df_dict,
                                                      profile=self._profile)
        except KeyError:
            raise ScrubberValidationError("{name} is not a valid type of rule".format(name=rule["rule_type"]))

    def _run_single_column_rule(self, rule, column, df_dict):
        """
        Run the cleansing of the rule against a job and DataFrame

        Parameters
        ----------
        rule: an object containing the configuration of the rule to be run
        column: the name of the column on which to run the rule
        df_dict: a dictionary of DataFrame used when the rule configuration
            references an external file
        """

        # run the rule. this function will return the DF with clean values
        # appended as an additional column and a reference list for auto matching
        logger.info("Running rule {0} on column {1}".format(rule["rule_type"], column))
        validator = self._get_validator(rule, df_dict)
        validator.run_all(self.df, column)
        logger.info("Completed rule {0} on column {1}".format(rule["rule_type"], column))

        # now copy the new data into the original column
        if "append_results" not in rule or rule["append_results"] is False:
            try:
                # in the case of an optional column, `column` is a label, not an index
                self.df.iloc[:, column] = self.df.iloc[:, -1]
                self.df.drop(self.df.columns[-1], axis=1, inplace=True)
            except ValueError:
                # if that is the case then either the dataframe is unchanged, or we have quarantined it.
                pass

    def _run_multi_column_rule(self, rule, df_dict):
        """
        Run the cleansing of a multi-column rule against a job and DataFrame

        Parameters
        ----------
        rule: an object containing the configuration of the rule to be run
        df_dict: a dictionary of DataFrames used when the rule configuration
            references an external file
        """
        logger.info("Running multi-column rule {0}".format(rule["rule_type"]))
        validator = self._get_validator(rule, df_dict)
        validator.run_all(self.df)
        logger.info("Completed multi-column rule {0}".format(rule["rule_type"]))

    def run(self, df, config, df_dict=None):
        """
        Cleanses a DataFrame in place according to the passed configuration

        Parameters
        ----------
        df: the DataFrame to be cleansed
        config: a config dict containing the configuration
        df_dict: a dictionary of any DataFrame references in the configuration
        """
        self._report_writer.reset_report()
        self.df = df

        if df_dict is None:
            df_dict = {}

        if self.df.shape[0] > self._profile.maximum_records:
            logger.info("Not processing job because too many records")
            raise ScrubberTooManyRecordsError(
                'There are too many records in the submitted file: please include no more '
                'than {0} records in your file'.format(self._profile.maximum_records))

        self.validate_config(config)

        # count the number of records and update the database

        original_total_columns = self.df.shape[1]
        for rule in config["rules"]:
            if self.df.shape[0] > 0:  # stop processing if all records have been deleted
                if "field" in rule and rule["field"] is not None:
                    try:
                        # if the 'field' is not in columns we cannot get_loc, but still need to pass on the name
                        # as we might be dealing with an optional column
                        column = df.columns.get_loc(get_column_name(self.df, rule["field"], original_total_columns))
                    except KeyError:
                        column = rule["field"]
                    self._run_single_column_rule(rule=rule,
                                                 column=column,
                                                 df_dict=df_dict)
                else:
                    self._run_multi_column_rule(rule=rule, df_dict=df_dict)

        return self._report_writer.get_report()

    def validate_config(self, config):
        """
        Checks that a passed configuration is valid and raises an exception if it is not

        Parameters
        ----------
        config: a config dict containing the configuration
        """

        try:
            for rule in config["rules"]:
                try:
                    self._get_validator(rule, {})
                except ScrubberValidationError as error:
                    if "field" in rule and rule["field"] is not None:
                        raise ScrubberValidationError("Error validating field {0}: {1}".format(rule["field"], error))
                    else:
                        raise ScrubberValidationError("Error validating multi-column rule for rule: {0} with error: {1}"
                                                      .format(rule, error))

        except KeyError:
            raise ScrubberValidationError("rules not present in config")

        return True

    def to_text(self, config):
        """
        Prints a config as human readable text

        :param config: the config to read
        :return: human readable text
        """

        self.validate_config(config)

        l = []
        for rule in config["rules"]:
            l.append(self._get_validator(rule, {}).get_dict(rule.get("field", "")))

        df = pd.DataFrame(l)
        df.set_index(["field", "type"], inplace=True)

        return df.to_csv()
