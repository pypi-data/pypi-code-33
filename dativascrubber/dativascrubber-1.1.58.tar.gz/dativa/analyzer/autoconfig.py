import logging
# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
#  This code is licensed under MIT license (see license.txt for details)

import re
import pandas as pd
from dativa.analyzer.analyzer import DataFrameAnalyzer
from dativa.scrubber.base import DateRangeType, FallbackType, SessionGapsType, SessionOverlapsType, DefaultProfile
from dativa.scrubber.validators import StringValidator, NumberValidator, DateValidator, LookupValidator, \
    UniqueFieldsValidator, SessionValidator
from dativa.tools.pandas import datetime_to_string

logger = logging.getLogger("dativa.analyzer.autoconfig")


class FileCounter:

    def __init__(self):
        self.df_dict = {}
        self.profile = DefaultProfile()
        self.maximum_string_length = 1024

    def clear_files(self):
        self.df_dict = {}

    def add_df(self, column, list_of_values):
        ix = "{0}.ref.csv".format("".join(c if c.isalnum() or c in ('.', '_') else '-' for c in column.name).strip())
        self.df_dict[ix] = pd.DataFrame(list_of_values, columns=[column.name])
        return ix


class AutoConfig:

    def __init__(self):
        self.files = FileCounter()
        self.maximum_string_length = 1024
        self.profile = DefaultProfile()

    @staticmethod
    def _get_attr(params, attr, default=None):
        if attr in params:
            return params[attr]
        else:
            if default is None:
                return ""
            else:
                return default

    @staticmethod
    def _get_fallback_mode(column):
        if column.fallback_mode == 'quarantine':
            return FallbackType.REMOVE_ENTRY
        elif column.fallback_mode == 'default':
            return FallbackType.USE_DEFAULT_VALUE
        elif column.fallback_mode == 'closest':
            return FallbackType.REMOVE_ENTRY

    def _trim_string(self, s):
        return s[0: self.maximum_string_length]

    @staticmethod
    def _finalise_params(validator, params, default_value=""):
        # remove any default values
        for a in list(params):
            if params[a] == validator.fields[a]["default"]:
                del params[a]

        # add the default for that fallback mode
        if "fallback_mode" in params and params["fallback_mode"] == "use_default":
            params["default_value"] = default_value

        return (params)

    def _get_string_params(self, column, max_references):
        regex = ".*"
        if 1 <= column.number_references <= max_references:
            regex = ""
            for r in column.reference_list:
                regex = regex + re.escape(r) + "|"
            regex = regex[:-1]
        return self._finalise_params(
            validator=StringValidator(),
            params={"minimum_length": column.min,
                    "maximum_length": column.max,
                    "attempt_closest_match": False,
                    "lookalike_match": False,
                    "fallback_mode": self._get_fallback_mode(column),
                    "skip_blank": column.has_blanks,
                    "is_unique": column.is_unique,
                    "regex": regex},

            default_value=self._trim_string(column.default_value))

    def _get_number_params(self, column):
        return self._finalise_params(
            validator=NumberValidator(),
            params={"decimal_places": column.decimal_places,
                    "fix_decimal_places": True,
                    "minimum_value": column.min,
                    "maximum_value": column.max,
                    "attempt_closest_match": False,
                    "lookalike_match": False,
                    "fallback_mode": self._get_fallback_mode(column),
                    "skip_blank": column.has_blanks,
                    "is_unique": column.is_unique},
            default_value=self._trim_string(column.default_value))

    def _get_date_params(self, column):
        return self._finalise_params(
            validator=DateValidator(),
            params={"date_format": column.date_format,
                    "range_check": DateRangeType.FIXED,
                    "range_minimum": datetime_to_string(column.min, column.date_format),
                    "range_maximum": datetime_to_string(column.max, column.date_format),
                    "attempt_closest_match": False,
                    "lookalike_match": False,
                    "fallback_mode": self._get_fallback_mode(column),
                    "skip_blank": column.has_blanks,
                    "is_unique": column.is_unique},
            default_value=self._trim_string(column.default_value))

    def _get_lookup_params(self, column):

        file = self.files.add_df(column, column.reference_list)

        attempt_closest_match = (column.fallback_mode == "closest")
        lookalike_match = (column.number_references < 50 and
                           column.sample_percent_blank * column.total_records < self.profile.maximum_records_lookalike)
        return self._finalise_params(
            validator=LookupValidator(),
            params={"original_reference": file,
                    "reference_field": 0,
                    "attempt_closest_match": attempt_closest_match,
                    "lookalike_match": lookalike_match,
                    "fallback_mode": self._get_fallback_mode(column),
                    "skip_blank": column.has_blanks},
            default_value=self._trim_string(column.default_value))

    def _get_rule(self, column, min_references, max_references):
        if column.type == 'string':
            if min_references <= column.number_references <= max_references:
                return {
                    "field": column.name,
                    "rule_type": "Lookup",
                    "params": self._get_lookup_params(column)
                }
            else:
                return {
                    "field": column.name,
                    "rule_type": "String",
                    "params": self._get_string_params(column, max_references)
                }

        if column.type == 'number':
            return {
                "field": column.name,
                "rule_type": "Number",
                "params": self._get_number_params(column)
            }

        if column.type == 'date':
            return {
                "field": column.name,
                "rule_type": "Date",
                "params": self._get_date_params(column)
            }

    @staticmethod
    def _concat_list(l, sep=","):
        s = ""
        for item in l:
            if item == l[-1]:
                return s + item
            else:
                s = s + item + sep

    def _get_unique_rule(self, analyser):
        cols = analyser.get_unique_columns(0.95, 5)
        if cols:
            unique_columns = self._concat_list(cols, ",")
            logger.info(
                "Added uniqueness rule to config")

            return {
                "rule_type": "Uniqueness",
                "params": self._finalise_params(validator=UniqueFieldsValidator(),
                                                params={
                                                    "unique_fields": unique_columns,
                                                    "use_last_value": True
                                                })
            }
        else:
            return None

    @staticmethod
    def _session_rule_is_good(df, session_params):
        number_rows = df.shape[0]

        number_clean_rows = SessionValidator(
            session_params).count_good_rows(df)

        logger.info("Session rule {0}, {1}, {2} has {3} good records".format(session_params["key_field"],
                                                                             session_params["start_field"],
                                                                             session_params["end_field"],
                                                                             number_clean_rows / number_rows * 100))
        if number_clean_rows > number_rows * 0.8:
            return True

        return False

    def _get_session_rule(self, df, rules):
        if len(rules) > 1:
            # more than one session rule so look for same formats
            candidate_columns = []
            for first_rule in rules:
                for second_rule in rules:
                    if first_rule["field"] != second_rule["field"] and first_rule["params"]["date_format"] == \
                            second_rule["params"]["date_format"]:
                        candidate_columns.append([first_rule, second_rule])

            for setting in [{'gaps': SessionGapsType.EXTEND_END, 'allowed_gap': 0},
                            {'gaps': SessionGapsType.EXTEND_END, 'allowed_gap': 1},
                            {'gaps': SessionGapsType.IGNORE, 'allowed_gap': 0}]:
                for candidate in candidate_columns:
                    for key in df.columns:
                        if key != candidate[0]["field"] and key != candidate[1]["field"]:
                            session_params = self._finalise_params(validator=SessionValidator(),
                                                                   params={"key_field": key,
                                                                           "start_field": candidate[0]["field"],
                                                                           "end_field": candidate[1]["field"],
                                                                           "allowed_gap_seconds": 0,
                                                                           "allowed_overlap_seconds": setting[
                                                                               'allowed_gap'],
                                                                           "gaps_option": setting['gaps'],
                                                                           "overlaps_option": SessionOverlapsType.TRUNCATE_END,
                                                                           "date_format": candidate[0]["params"][
                                                                               "date_format"],
                                                                           "remove_zero_length": True})

                            if self._session_rule_is_good(df, session_params):
                                logger.info("Added session rule to config")
                                return {"rule_type": "Session",
                                        "params": session_params}
        return None

    def create_config(self,
                      df,
                      profile=None,
                      csv_delimiter=',',
                      maximum_string_length=1024,
                      large_sample_size=5000,
                      small_sample_size=100,
                      clean_threshold=0.95,
                      outlier_threshold=2,
                      min_occurences=5,
                      min_references=10,
                      max_references=1000):

        self.files.clear_files()
        if profile is not None:
            self.profile = profile
        self.maximum_string_length = maximum_string_length

        """Auto config create rules."""

        # delete any existing rules.
        config = {"rules": []}

        # analyse the dataframe
        analyser = DataFrameAnalyzer(df=df,
                                     large_sample_size=large_sample_size,
                                     small_sample_size=small_sample_size,
                                     clean_threshold=clean_threshold,
                                     outlier_threshold=outlier_threshold,
                                     min_occurences=min_occurences)

        # create rules appropriate for each column
        date_rules = []
        has_unique = False
        for column in analyser.columns:
            has_unique = has_unique or column.is_unique
            rule = self._get_rule(column, min_references, max_references)
            logger.info("Added {0} rule to config".format(rule["rule_type"]))
            config["rules"].append(rule)

            if rule["rule_type"] == 'Date':
                date_rules.append(rule)

        # create unique columns
        if not has_unique:
            unique_rule = self._get_unique_rule(analyser)
            if unique_rule is not None:
                config["rules"].append(unique_rule)

        # add session rules...
        session_rule = self._get_session_rule(df, date_rules)
        if session_rule is not None:
            config["rules"].append(session_rule)

        return config, self.files.df_dict

    def describe_dataframe(self, config, df_dict):

        s = "column,type,minimum,maximum,format,has_blanks\n"
        extra = "\n"
        for rule in config["rules"]:
            params = self._get_attr(rule, "params")
            column = self._get_attr(rule, "field")
            rule_type = self._get_attr(rule, "rule_type")
            if rule_type == "Date":
                s = s + "{column},{type},{minimum},{maximum},{format},{has_blanks}\n".format(
                    column=column,
                    type=rule_type,
                    minimum=self._get_attr(params, "range_minimum"),
                    maximum=self._get_attr(params, "range_maximum"),
                    format=self._get_attr(params, "date_format"),
                    has_blanks=self._get_attr(params, "skip_blank", False))

            elif rule_type == "String":
                s = s + "{column},{type},{minimum},{maximum},{format},{has_blanks}\n".format(
                    column=column,
                    type=rule_type,
                    minimum=self._get_attr(params, "minimum_length"),
                    maximum=self._get_attr(params, "maximum_length"),
                    format='',
                    has_blanks=self._get_attr(params, "skip_blank", False))

            elif rule_type == "Number":
                if self._get_attr(params, "decimal_places") == 0:
                    frm = "int"
                else:
                    frm = "0." + "0" * self._get_attr(params, "decimal_places")

                s = s + "{column},{type},{minimum},{maximum},{format},{has_blanks}\n".format(
                    column=column,
                    type=rule_type,
                    minimum=self._get_attr(params, "minimum_value"),
                    maximum=self._get_attr(params, "maximum_value"),
                    format=frm,
                    has_blanks=self._get_attr(params, "skip_blank", False))

            elif rule_type == "Lookup":
                s = s + "{column},{type},{minimum},{maximum},{format},{has_blanks}\n".format(
                    column=column,
                    type="String",
                    minimum=df_dict[params["original_reference"]
                            ].iloc[:, 0].min().replace(",", "_"),
                    maximum=df_dict[params["original_reference"]
                            ].iloc[:, 0].max().replace(",", "_"),
                    format="Lookup",
                    has_blanks=self._get_attr(params, "skip_blank", False))

            elif rule_type == "Uniqueness":
                extra = extra + "Unique on {uniques}\n".format(
                    uniques=self._get_attr(params, "unique_fields"))

            elif rule_type == "Session":
                extra = extra + "Session rule on {start}, {stop} with unique id {id}\n".format(
                    start=self._get_attr(params, "start_field"),
                    stop=self._get_attr(params, "end_field"),
                    id=self._get_attr(params, "key_field"))

        return s + extra
