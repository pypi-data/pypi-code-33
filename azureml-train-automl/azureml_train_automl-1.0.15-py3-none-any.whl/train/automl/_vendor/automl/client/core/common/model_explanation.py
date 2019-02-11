# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""model_explanation.py, A file for model explanation classes."""

from automl.client.core.common import constants


# TODO: Tell PowerBI to fix casing on their end
class FeatureNameFormats(object):
    """Feature name formats."""

    STRING = 'str'
    JSON = 'json'

    ALL = {STRING, JSON}


class Explanation(object):
    """A wrapper class which contains all model explanation related information."""

    def __init__(self,
                 task_type,
                 shap_values=None,
                 expected_values=None,
                 overall_summary=None,
                 overall_imp=None,
                 per_class_summary=None,
                 per_class_imp=None):
        """Init method for the Explanation class."""
        self.task_type = task_type
        self.shap_values = shap_values
        self.expected_values = expected_values
        self.overall_summary = overall_summary
        self.overall_imp = overall_imp
        self.per_class_summary = per_class_summary
        self.per_class_imp = per_class_imp

    def get_model_explanation(self,
                              feature_name_format=FeatureNameFormats.STRING,
                              transformer=None):
        """
        Get model explanation.

        :param feature_name_format: feature name's format, either str or json
        :param transformer: the DataTransformer used in preprocessing to
            generate features, if applicable
        :type transformer: DataTransformer
        :return: model explanations information with feature names in specified
            format
        """
        # TODO: Remove .lower() after PowerBI fixes casing
        if feature_name_format.lower() not in FeatureNameFormats.ALL:
            raise ValueError('Invalid feature name format specified. Value'
                             'must be in the set {}'
                             .format(FeatureNameFormats.ALL))

        if feature_name_format.lower() == FeatureNameFormats.STRING or \
                transformer is None:
            overall_imp_format = self.overall_imp
            per_class_imp_format = self.per_class_imp
        else:
            overall_imp_format = \
                transformer.get_json_strs_for_engineered_feature_names(
                    self.overall_imp)
            per_class_imp_format = None
            if self.task_type == constants.Tasks.CLASSIFICATION:
                per_class_imp_format = []
                for item in self.per_class_imp:
                    per_class_imp_format.append(
                        transformer.get_json_strs_for_engineered_feature_names(
                            item))
        return self.shap_values, self.expected_values, self.overall_summary, \
            overall_imp_format, self.per_class_summary, per_class_imp_format
