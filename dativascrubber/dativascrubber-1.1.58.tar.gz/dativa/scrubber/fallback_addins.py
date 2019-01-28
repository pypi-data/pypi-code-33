# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
#  This code is licensed under MIT license (see license.txt for details)

import logging
import pandas as pd
import numpy as np
from dativa.tools.pandas import get_column_name, get_unique_column_name
from .distance import get_closest_match, run_lookalike
from .base import BaseAddIn, HistoryType, FallbackType

logger = logging.getLogger("dativa.scrubber.fallback")


class BestMatchesAddIn(BaseAddIn):
    """
    AddIn to add functionality to a Validator that sets unknown values to the closest value
    """

    fields = {'attempt_closest_match': {
        "default": False, "validator": lambda x: x in [True, False]},
        'string_distance_threshold': {
            "default": 0.7, "validator": lambda x: (0 <= x <= 1)}}

    def _apply_best_matches(self, df, source_column, destination_column, reference_list, string_distance_threshold):
        """
        Copies the closest matching item from a reference list into the destination column
        in the current DataFrame. The reference list is matched against all values in the original
        DataFrame where the source column is not null and the destination column is.

        Parameters
        ----------
        df: the DataFrame
        source_column: the name of the source column in the DataFrame
        destination_column: the name of the destination column in the reference_list to use for best matches
        reference_list: a series contains the list of potential best matches
        string_distance_threshold: the threshold at which best matches
            are applied
        """

        if len(reference_list) > 0:

            source = get_column_name(df, source_column)
            destination = get_column_name(df, destination_column)

            logger.info("Applying best matches to rule {0} on column {1}".format(
                self.validator.rule_type, source_column))

            source_values = df.loc[df[destination].isnull(
            ) & df[source].notnull(), source].unique()

            if 0 < len(source_values) < self.validator.profile.maximum_records_closest_matches:
                source_values_df = pd.DataFrame(
                    source_values, columns=[source], dtype=pd.np.str)
                # create the possible substitutions objects in reverse order
                source_values_df["clean"], source_values_df["distance"] = get_closest_match(
                    source_values, reference_list.values)
                merged_df = df.loc[:, [source]].reset_index().merge(
                    source_values_df, how='left', left_on=source, right_on=source).set_index('index')
                merged_df.loc[merged_df["distance"] >
                              float(string_distance_threshold), "replace"] = merged_df["clean"]
                if merged_df[merged_df["replace"].notnull()].shape[0] > 0:
                    df.loc[merged_df["clean"].notnull(
                    ), destination] = merged_df["replace"]

                    self.report_writer.log_history(
                        self.validator.rule_type,
                        get_column_name(df, source_column),
                        df[merged_df["replace"].notnull(
                        )],
                        HistoryType.REPLACED,
                        "Best match")

            else:
                logger.info("Skipped best matches for rule {0} on column {1}".format(
                    self.validator.rule_type, source_column))

    def run(self, df, column, original_column):

        if self.validator.reference_list is not None and self.validator.attempt_closest_match:
            # apply the best matches from the invalid records for now...
            self._apply_best_matches(df,
                                     original_column,
                                     column,
                                     self.validator.reference_list,
                                     self.validator.string_distance_threshold)


class LookalikeAddIn(BaseAddIn):
    """
    AddIn to add functionality to a Validator that sets unknown values to the closest vlaue according
    to a lookalike match
    """

    fields = {'lookalike_match': {
        "default": False, "validator": lambda x: x in [True, False]},
        'string_distance_threshold': {
            "default": 0.7, "validator": lambda x: (0 <= x <= 1)}}

    @staticmethod
    def _get_lookalike_matrix(df, cols_to_compare, target_field):
        """
        Return a numpy matrix suitable for lookalike matching containing:
        - the strings to be used for the lookalike match, which are concatenated
          strings in all the relevant columns to compare
        - the values of the target field
        - a blank column of int64
        - a blank column of strings
        """
        return np.vstack((df[cols_to_compare].T.apply(str).values,
                          df[target_field].apply(str).values,
                          np.zeros((1, df.shape[0]), dtype=np.int64),
                          np.zeros((1, df.shape[0]), dtype=np.str)
                          ))

    def _apply_lookalikes(self, df, source_column, destination_column, string_distance_threshold):
        """
        Copies the value from the closest matching row into the destination column.

        Parameters
        ----------
        df: the DataFrame
        source_column: the name of the source column in the DataFrame,
            this is ignored in the lookalike match
        destination_column: the name of the destination column
        string_distance_threshold: the threshold at which best matches
            are applied
        """

        logger.info("Applying lookalikes to rule {0} on column {1}".format(
            self.validator.rule_type, source_column))

        # prepare the columns....
        source = get_column_name(df, source_column)
        destination = get_column_name(df, destination_column)
        lookalike_column = get_unique_column_name(df, "lookalike")

        # check there are sufficient clean records for the match...
        number_to_match = df[df[destination].isnull()].shape[0]
        total_records = df.shape[0]

        number_possible_records = total_records - number_to_match
        if number_possible_records > self.validator.profile.lookalike_number_records:
            number_possible_records = self.validator.profile.lookalike_number_records

        if (number_to_match < self.validator.profile.maximum_records_lookalike and
                df.shape[1] > 1 and
                df.shape[0] < self.validator.profile.maximum_file_records_lookalike):

            # run the lookalike
            cols_to_compare = df.columns
            cols_to_compare = cols_to_compare.drop(destination)
            cols_to_compare = cols_to_compare.drop(source)
            df[lookalike_column] = run_lookalike(matrix=self._get_lookalike_matrix(df, cols_to_compare, destination),
                                                 rows_to_match=df[destination].isnull(
                                                 ).values,
                                                 top_n=number_possible_records,
                                                 threshold=float(string_distance_threshold))

            # update the clean column and log the history....
            df.loc[df[lookalike_column] != '',
                   destination] = df[lookalike_column]

            if df[df[lookalike_column] != ''].shape[0] > 0:
                self.report_writer.log_history(
                    self.validator.rule_type,
                    get_column_name(df, source_column),
                    df[df[lookalike_column] !=
                       ''][[source, destination]],
                    HistoryType.REPLACED,
                    "Lookalike match")

            # remove the lookalike column...
            df.drop(lookalike_column, axis=1, inplace=True)
        else:
            logger.info("Skipped lookalikes for rule {0} on column {1}".format(
                self.validator.rule_type, source_column))

    def run(self, df, column, original_column=None):

        if self.validator.lookalike_match:
            self._apply_lookalikes(df,
                                   original_column,
                                   column,
                                   self.validator.string_distance_threshold)


class FallbackAddIn(BaseAddIn):
    """
    AddIn to add functionality to a Validator to set unmatched values according to the fallback
    modes
    """

    fields = {'fallback_mode': {"default": None, "validator": lambda x: x in [
        FallbackType.USE_DEFAULT_VALUE, FallbackType.USE_INVALID_DATA, FallbackType.REMOVE_ENTRY]},
              'default_value': {
                  "default": "", "validator": lambda x: True}}

    def _apply_fallback_values(self, df, original_column, transformed_column, fallback_mode, default_value):
        """
        Sets any NULL values in the passed columns to the appropriate value

        Parameters
        ----------
        df: the DataFrame to run
        original_column, transformed_column: the column running on
        fallback_mode: one of three options:
            FallbackType.USE_DEFAULT_VALUE - replaces the Nulls with the specified default
            FallbackType.USE_INVALID_DATA - leaves the invalid data unchanged
            FallbackType.REMOVE_ENTRY - removes the invalid data and adds to quarantine
        default_value: the default value

        """
        rows = df.loc[df.iloc[:, -1].isnull()]

        logger.info("Applying fallback to {2}, mode {3} on rule {0} on column {1}".format(
            self.validator.rule_type, original_column, rows.shape[0], FallbackType.pretty(fallback_mode)))

        if rows.shape[0] > 0:

            if fallback_mode == FallbackType.USE_DEFAULT_VALUE:
                # set any empty rows in the final column to the default value
                df.loc[rows.index, transformed_column] = default_value
                self.report_writer.log_history(
                    self.validator.rule_type,
                    get_column_name(df, original_column),
                    df.loc[rows.index, [original_column, transformed_column]],
                    HistoryType.REPLACED,
                    FallbackType.pretty(fallback_mode)
                )

            elif fallback_mode == FallbackType.USE_INVALID_DATA:
                # set any empty rows in the final column to the  original value
                df.loc[rows.index, transformed_column] = df.loc[:, original_column]
                self.report_writer.log_history(
                    self.validator.rule_type,
                    get_column_name(df, original_column),
                    df.loc[rows.index, [original_column, transformed_column]],
                    HistoryType.IGNORED,
                    FallbackType.pretty(fallback_mode)
                )

            # remove nulls if replacement mode is to remove
            elif fallback_mode == FallbackType.REMOVE_ENTRY:
                self.report_writer.log_history(
                    self.validator.rule_type,
                    get_column_name(df, original_column),
                    df.loc[rows.index],
                    HistoryType.REMOVED,
                    FallbackType.pretty(fallback_mode)
                )

                df.drop(rows.index, inplace=True)

    def run(self, df, column, original_column=None):

        # put in any default values if present
        self._apply_fallback_values(df,
                                    original_column,
                                    column,
                                    self.validator.fallback_mode,
                                    self.validator.default_value)


class SkipBlankAddIn(BaseAddIn):
    """
    Adds functionality to a Validator to skip blanks
    """

    fields = {'skip_blank': {
        "default": False, "validator": lambda x: x in [True, False]}}

    @staticmethod
    def _copy_blanks(df, source_column, destination_column):
        """
        Copies all blanks from the source column to the destination column
        """
        df.loc[df.loc[:, source_column].isnull(), destination_column] = ''

        if df.dtypes[source_column] == object:
            df.loc[(df.loc[:, source_column] == ''), destination_column] = ''

    def run(self, df, column, original_column=None):

        if self.validator.skip_blank is True:
            self._copy_blanks(df, original_column, column)
