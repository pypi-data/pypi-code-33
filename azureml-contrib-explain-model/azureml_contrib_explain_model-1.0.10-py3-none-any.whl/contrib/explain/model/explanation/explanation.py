# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the explanations that are returned from explaining models."""

import os
import numpy as np

from azureml._restclient.assets_client import AssetsClient
from azureml._restclient.constants import RUN_ORIGIN
from azureml.explain.model._internal.common import _sort_features, _sort_feature_list_multiclass, \
    _order_imp
from azureml.explain.model._internal.model_summary import ModelSummary
from azureml._logging import ChainedIdentity
from azureml.explain.model._internal.constants import Dynamic, ExplainParams, ExplanationParams, ExplainType, History

from ..common.explanation_utils import ArtifactUploader


class BaseExplanation(ChainedIdentity):
    """Defines the common explanation returned by explainers."""

    def __init__(self, features=None, **kwargs):
        """Create the common explanation from the given feature names.

        :param features: The feature names.
        :type features: Union[list[str], list[int]]
        """
        super(BaseExplanation, self).__init__(**kwargs)
        self._logger.debug('Initializing BaseExplanation')
        self._features = features

    @property
    def features(self):
        """Get the feature names.

        :return: The feature names.
        :rtype: list[str]
        """
        return self._features


class LocalExplanation(BaseExplanation):
    """Defines the common local explanation returned by explainers."""

    def __init__(self, local_importance_values=None, **kwargs):
        """Create the local explanation from the explainer's feature importance values.

        :param local_importance_values: The feature importance values.
        :type local_importance_values: numpy.ndarray
        """
        super(LocalExplanation, self).__init__(**kwargs)
        self._logger.debug('Initializing LocalExplanation')
        self._local_importance_values = local_importance_values

    @property
    def local_importance_values(self):
        """Get the feature importance values.

        :return: For a model with a single output such as regression, this
            returns a list of feature importance values. For models with vector outputs this function
            returns a list of such lists, one for each output. The dimension of this matrix
            is (# examples x # features).
        :rtype: list[float]
        """
        return self._local_importance_values


class GlobalExplanation(BaseExplanation):
    """Defines the common global explanation returned by explainers."""

    def __init__(self, global_importance_values=None, global_importance_rank=None, **kwargs):
        """Create the global explanation from the explainer's overall importance values and order.

        :param global_importance_values: The feature importance values.
        :type global_importance_values: numpy.ndarray
        :param global_importance_rank: The feature indexes sorted by importance.
        :type global_importance_rank: numpy.ndarray
        """
        super(GlobalExplanation, self).__init__(**kwargs)
        self._logger.debug('Initializing GlobalExplanation')
        self._global_importance_values = global_importance_values
        self._global_importance_rank = global_importance_rank.tolist()
        if self._features is not None:
            self._logger.debug('Features stored on explanation as strings')
            self._global_importance_names = _sort_features(self._features, global_importance_rank).tolist()
        else:
            # order of importance
            self._logger.debug('No features available, instead returning feature indices')
            self._global_importance_names = global_importance_rank.tolist()

    @property
    def global_importance_values(self):
        """Get the overall feature importance values.

        :return: The model level feature importance values sorted in
            descending order.
        :rtype: list[float]
        """
        return self._global_importance_values

    @property
    def global_importance_names(self):
        """Get the sorted overall feature importance names.

        :return: The feature names sorted by importance, or if names not provided same as rank.
        :rtype: Union[list[str], list[int]]
        """
        return self._global_importance_names

    @property
    def global_importance_rank(self):
        """Get the overall feature importance rank or indexes.

        :return: The feature indexes sorted by importance.
        :rtype: list[int]
        """
        return self._global_importance_rank


class TextExplanation(LocalExplanation):
    """Defines the mixin for text explanations."""

    def __init__(self, **kwargs):
        """Create the text explanation."""
        super(TextExplanation, self).__init__(**kwargs)
        order = _order_imp(np.abs(self.local_importance_values))
        self._local_importance_rank = _sort_features(self._features, order).tolist()
        self._logger.debug('Initializing TextExplanation')
        if len(order.shape) == 3:
            i = np.arange(order.shape[0])[:, np.newaxis]
            j = np.arange(order.shape[1])[:, np.newaxis]
            self._ordered_local_importance_values = np.array(self.local_importance_values)[i, j, order]
        else:
            self._ordered_local_importance_values = self.local_importance_values

    @property
    def local_importance_rank(self):
        """Feature names sorted by importance.

        This property exists for text explanations only and not for local because currently
        we are doing text explanations for a single document and it is more difficult to
        define order for multiple instances.  Note this is subject to change if we eventually
        add global explanations for text explainers.

        :return: The feature names sorted by importance.
        :rtype: list
        """
        return self._local_importance_rank

    @property
    def ordered_local_importance_values(self):
        """Get the feature importance values ordered by importance.

        This property exists for text explanations only and not for local because currently
        we are doing text explanations for a single document and it is more difficult to
        define order for multiple instances.  Note this is subject to change if we eventually
        add global explanations for text explainers.

        :return: For a model with a single output such as regression, this
            returns a list of feature importance values. For models with vector outputs this function
            returns a list of such lists, one for each output. The dimension of this matrix
            is (# examples x # features).
        :rtype: list
        """
        return self._ordered_local_importance_values


class ExpectedValuesMixin(object):
    """Defines the mixin for expected values."""

    def __init__(self, expected_values=None, **kwargs):
        """Create the expected values mixin and set the expected values.

        :param expected_values: The expected values of the model.
        :type expected_values: list
        """
        super(ExpectedValuesMixin, self).__init__(**kwargs)
        self._expected_values = expected_values

    @property
    def expected_values(self):
        """Get the expected values.

        :return: The expected value of the model applied to the set of initialization examples.
        :rtype: list
        """
        return self._expected_values


class ClassesMixin(object):
    """Defines the mixin for classes.

    This mixin is added when the user specifies classes in the classification
    scenario when creating a global or local explanation.
    This is activated when the user specifies the classes parameter for global
    or local explanations.
    """

    def __init__(self, classes=None, **kwargs):
        """Create the classes mixin and set the classes.

        :param classes: Class names as a list of strings. The order of
            the class names should match that of the model output.
        :type classes: list[str]
        """
        super(ClassesMixin, self).__init__(**kwargs)
        self._classes = classes

    @property
    def classes(self):
        """Get the classes.

        :return: The list of classes.
        :rtype: list
        """
        return self._classes


class PerClassMixin(ClassesMixin):
    """Defines the mixin for per class aggregated information.

    This mixin is added for the classification scenario for global
    explanations.  The per class importance values are group averages of
    local importance values across different classes.
    """

    def __init__(self, per_class_names=None, per_class_values=None, per_class_rank=None, **kwargs):
        """Create the per class mixin.

        :param per_class_names: The per class importance feature names.
        :type per_class_names: list
        :param per_class_values: The per class importance values.
        :type per_class_values: list
        :param per_class_rank: The per class importance rank or indexes.
        :type per_class_rank: list
        """
        super(PerClassMixin, self).__init__(**kwargs)
        self._per_class_names = per_class_names
        self._per_class_values = per_class_values
        self._per_class_rank = per_class_rank

    @property
    def per_class_names(self):
        """Get the per class importance features.

        :return: The per class feature names sorted in the same order as in per_class_values
            or the indexes that would sort per_class_values.
        :rtype: list
        """
        return self._per_class_names

    @property
    def per_class_values(self):
        """Get the per class importance values.

        :return: The model level per class feature importance values sorted in
            descending order.
        :rtype: list
        """
        return self._per_class_values

    @property
    def per_class_rank(self):
        """Get the per class importance rank or indexes.

        :return: The per class indexes that would sort per_class_values.
        :rtype: list
        """
        return self._per_class_rank


class HasScoringModel(object):
    """Defines an explanation that can be operationalized for real-time scoring."""

    def __init__(self, scoring_model=None, **kwargs):
        """Create the operationalization explanation from scoring model.

        :param scoring_model: The scoring model.
        :type scoring_model: ScoringModel
        """
        super(HasScoringModel, self).__init__(**kwargs)
        self._scoring_model = scoring_model

    @property
    def scoring_model(self):
        """Return the scoring model.

        :rtype: ScoringModel
        :return: The scoring model.
        """
        return self._scoring_model


def upload_model_explanation(run, explanation, **kwargs):
    """Upload the model explanation information to run history.

    :param run: A model explanation run to save explanation information to.
    :type run: azureml.core.run.Run
    :param explanation: The explanation information to save.
    :type explanation: BaseExplanation
    """
    uploader = ArtifactUploader(run, **kwargs)
    assets_client = AssetsClient.create(run.experiment.workspace)
    text_explanation = isinstance(explanation, TextExplanation)
    classification = isinstance(explanation, ClassesMixin)
    if classification:
        model_type = ExplainType.CLASSIFICATION
    else:
        model_type = ExplainType.REGRESSION
    if text_explanation:
        explainer_type = ExplainType.TEXT
    else:
        explainer_type = ExplainType.TABULAR
    # save model type and explainer type
    run.add_properties({ExplainType.MODEL: model_type, ExplainType.EXPLAINER: explainer_type})
    # upload the shap values, overall summary, per class summary and feature names
    upload_dir = uploader._create_upload_dir()
    # TODO what if we're using lime?
    explanation._logger.debug('Uploading shap values and expected values as artifacts')
    summary_object = ModelSummary()
    if isinstance(explanation, LocalExplanation):
        # TODO remove this (can't right now because of get_model_summary)
        uploader._upload_artifact(upload_dir, History.SHAP_VALUES, explanation.local_importance_values)
        # upload local importance/shap value information
        shap_values_artifacts = uploader._get_model_summary_artifacts(upload_dir,
                                                                      History.SHAP_VALUES,
                                                                      np.array(explanation.local_importance_values))
        summary_object.add_from_get_model_summary(History.SHAP_VALUES, shap_values_artifacts)

    if isinstance(explanation, ExpectedValuesMixin) and explanation.expected_values is not None:
        # upload expected value (shap specific) information
        uploader._upload_artifact(upload_dir, History.EXPECTED_VALUES, explanation.expected_values)
        expected_values_artifact_info = [{
            History.PREFIX: os.path.normpath('{}/{}/{}/{}'.format(RUN_ORIGIN,
                                                                  run.id,
                                                                  upload_dir,
                                                                  History.EXPECTED_VALUES))
        }]
        expected_values_metadata_info = {
            History.NAME: History.EXPECTED_VALUES
        }
        summary_object.add_from_get_model_summary(History.EXPECTED_VALUES,
                                                  (expected_values_artifact_info, expected_values_metadata_info))

    if isinstance(explanation, GlobalExplanation):
        if explanation.features is not None:
            explanation._logger.debug('Uploading features as artifact and ordered features to asset')
            # upload features
            uploader._upload_artifact(upload_dir, History.FEATURES, explanation.features)
            features_artifact_info = [{
                History.PREFIX: os.path.normpath('{}/{}/{}/{}'.format(RUN_ORIGIN,
                                                                      run.id,
                                                                      upload_dir,
                                                                      History.FEATURES))
            }]
            features_metadata_info = {
                History.NAME: History.FEATURES
            }
            summary_object.add_from_get_model_summary(History.FEATURES,
                                                      (features_artifact_info, features_metadata_info))

            # upload global ordered feature names
            if isinstance(explanation.global_importance_names[0], str):
                global_ordered_features = explanation.global_importance_names
            else:
                global_ordered_features = _sort_features(explanation.features,
                                                         explanation.global_importance_rank).tolist()
            global_importance_name_artifacts = uploader._get_model_summary_artifacts(upload_dir,
                                                                                     History.GLOBAL_IMPORTANCE_NAMES,
                                                                                     np.array(global_ordered_features))
            summary_object.add_from_get_model_summary(History.GLOBAL_IMPORTANCE_NAMES,
                                                      global_importance_name_artifacts)

            if classification and isinstance(explanation, PerClassMixin):
                # upload per class ordered feature names
                if isinstance(explanation.per_class_names[0], str):
                    per_class_ordered_features = explanation.per_class_importance_names
                else:
                    per_class_ordered_features = _sort_feature_list_multiclass(explanation.features,
                                                                               explanation.per_class_rank)
                per_class_importance_name_artifacts = \
                    uploader._get_model_summary_artifacts(upload_dir,
                                                          History.PER_CLASS_NAMES,
                                                          np.array(per_class_ordered_features))
                summary_object.add_from_get_model_summary(History.PER_CLASS_NAMES,
                                                          per_class_importance_name_artifacts)

        # upload global feature ranks
        global_importance_rank_artifacts = \
            uploader._get_model_summary_artifacts(upload_dir,
                                                  History.GLOBAL_IMPORTANCE_RANK,
                                                  np.array(explanation.global_importance_rank))
        summary_object.add_from_get_model_summary(History.GLOBAL_IMPORTANCE_RANK,
                                                  global_importance_rank_artifacts)

        # upload global feature importances
        global_importance_value_artifacts = \
            uploader._get_model_summary_artifacts(upload_dir,
                                                  History.GLOBAL_IMPORTANCE_VALUES,
                                                  explanation.global_importance_values)
        summary_object.add_from_get_model_summary(History.GLOBAL_IMPORTANCE_VALUES, global_importance_value_artifacts)

        if classification and isinstance(explanation, PerClassMixin):
            # upload per class feature ranks
            per_class_rank_artifacts = uploader._get_model_summary_artifacts(upload_dir,
                                                                             History.PER_CLASS_RANK,
                                                                             explanation.per_class_rank)
            summary_object.add_from_get_model_summary(History.PER_CLASS_RANK,
                                                      per_class_rank_artifacts)

            # upload per class importances
            per_class_value_artifacts = uploader._get_model_summary_artifacts(upload_dir,
                                                                              History.PER_CLASS_VALUES,
                                                                              explanation.per_class_values)
            summary_object.add_from_get_model_summary(History.PER_CLASS_VALUES, per_class_value_artifacts)

    if classification and explanation.classes is not None:
        # upload class information
        classes = explanation.classes
        if isinstance(classes, np.ndarray):
            classes = classes.tolist()
        explanation._logger.debug('Uploading class information')
        uploader._upload_artifact(upload_dir, History.CLASSES, classes)
        class_artifact_info = [{History.PREFIX: os.path.normpath('{}/{}/{}/{}'.format(RUN_ORIGIN,
                                                                                      run.id,
                                                                                      upload_dir,
                                                                                      History.CLASSES))}]
        class_metadata_info = {
            History.NAME: History.CLASSES,
            History.NUM_CLASSES: len(classes)
        }
        summary_object.add_from_get_model_summary(History.CLASSES, (class_artifact_info, class_metadata_info))

    # upload rich metadata information
    uploader._upload_artifact(upload_dir, History.RICH_METADATA, summary_object.get_metadata_dictionary())
    artifact_list = summary_object.get_artifacts()
    artifact_path = os.path.normpath('{}/{}/{}/{}'.format(RUN_ORIGIN, run.id, upload_dir, History.RICH_METADATA))

    artifact_list.append({History.PREFIX: artifact_path})
    assets_client.create_asset(
        History.EXPLANATION_ASSET,
        summary_object.get_artifacts(),
        metadata_dict={
            ExplainType.MODEL: ExplainType.CLASSIFICATION if classification else ExplainType.REGRESSION,
            ExplainType.DATA: explainer_type,
            ExplainType.EXPLAIN: ExplainType.SHAP,
            History.METADATA_ARTIFACT: artifact_path,
            History.VERSION: History.EXPLANATION_ASSET_TYPE_V2},
        run_id=run.id,
        properties={History.TYPE: History.EXPLANATION}
    )


def create_local_explanation(expected_values=None, classification=True,
                             scoring_model=None, text_explanation=False, **kwargs):
    """Dynamically creates an explanation based on local type and specified data.

    :param expected_values: The expected values of the model.
    :type expected_values: list
    :param classification: Indicates if this is a classification or regression explanation.
    :type classification: bool
    :param scoring_model: The scoring model.
    :type scoring_model: ScoringModel
    :param text_explanation: Indicates if this is a text explanation.
    :type text_explanation: bool
    """
    if text_explanation:
        mixins = [TextExplanation]
    else:
        mixins = [LocalExplanation]
    if expected_values is not None:
        mixins.append(ExpectedValuesMixin)
        kwargs[ExplanationParams.EXPECTED_VALUES] = expected_values
    if scoring_model is not None:
        mixins.append(HasScoringModel)
        kwargs[ExplainParams.SCORING_MODEL] = scoring_model
    if classification:
        mixins.append(ClassesMixin)
    DynamicLocalExplanation = type(Dynamic.LOCAL_EXPLANATION, tuple(mixins), {})
    local_explanation = DynamicLocalExplanation(**kwargs)
    return local_explanation


def create_global_explanation(local_explanation=None, expected_values=None,
                              classification=True, scoring_model=None,
                              text_explanation=False, **kwargs):
    """Dynamically creates an explanation based on global type and specified data.

    :param local_explanation: The local explanation information to include with global,
        can be done when the global explanation is a summary of local explanations.
    :type local_explanation: LocalExplanation
        :param expected_values: The expected values of the model.
        :type expected_values: list
    :param classification: Indicates if this is a classification or regression explanation.
    :type classification: bool
    :param scoring_model: The scoring model.
    :type scoring_model: ScoringModel
    :param text_explanation: Indicates if this is a text explanation.
    :type text_explanation: bool
    """
    mixins = [GlobalExplanation]
    # Special case: for aggregate explanations, we can include both global
    # and local explanations for the user as an optimization, so they
    # don't have to call both explain_global and explain_local and redo the
    # same computation twice
    if local_explanation is not None:
        mixins.append(LocalExplanation)
        kwargs[ExplainParams.LOCAL_IMPORTANCE_VALUES] = local_explanation.local_importance_values
    # In the mimic case, we don't aggregate so we can't have per class information
    # but currently in other cases when we aggregate local explanations we get per class
    if classification:
        if local_explanation is not None:
            mixins.append(PerClassMixin)
        else:
            mixins.append(ClassesMixin)
    if expected_values is not None:
        mixins.append(ExpectedValuesMixin)
        kwargs[ExplanationParams.EXPECTED_VALUES] = expected_values
    if scoring_model is not None:
        mixins.append(HasScoringModel)
        kwargs[ExplainParams.SCORING_MODEL] = scoring_model
    DynamicGlobalExplanation = type(Dynamic.GLOBAL_EXPLANATION, tuple(mixins), {})
    global_explanation = DynamicGlobalExplanation(**kwargs)
    return global_explanation


def aggregate_global_from_local_explanation(local_explanation=None, include_local=True,
                                            top_k=None, features=None, **kwargs):
    """Aggregate the local explanation information to global through averaging.

    :param local_explanation: The local explanation to summarize.
    :type local_explanation: LocalExplanation
    :param include_local: Whether the global explanation should also include local information.
    :type include_local: bool
    :param top_k: An integer that indicates the number of the most important features to return.
    :type top_k: int
    :param features: A list of feature names.
    :type features: list[str]
    """
    features = local_explanation.features
    kwargs[ExplainParams.FEATURES] = features
    local_importance_values = local_explanation.local_importance_values
    classification = isinstance(local_explanation, ClassesMixin)
    projection_required = top_k is not None
    if classification:
        # calculate the summary
        per_class_values = np.mean(np.absolute(local_importance_values), axis=1)
        row_indexes = np.arange(len(per_class_values))[:, np.newaxis]
        per_class_rank = _order_imp(per_class_values)
        global_importance_values = np.mean(per_class_values, axis=0)
        global_importance_rank = _order_imp(global_importance_values)
        if projection_required and len(global_importance_rank) > top_k:
            global_importance_rank = global_importance_rank[0:top_k]
            per_class_rank = per_class_rank[:, 0:top_k]
        # sort the per class summary
        per_class_values = per_class_values[row_indexes, per_class_rank]
        # sort the overall summary
        global_importance_values = global_importance_values[global_importance_rank]
        if features is not None:
            per_class_names = _sort_features(features, per_class_rank)
        else:
            # return order of importance
            per_class_names = per_class_rank
        kwargs[ExplainParams.PER_CLASS_NAMES] = per_class_names
        kwargs[ExplainParams.PER_CLASS_VALUES] = per_class_values
        kwargs[ExplainParams.PER_CLASS_RANK] = per_class_rank
    else:
        global_importance_values = np.mean(np.absolute(local_importance_values), axis=0)
        global_importance_rank = _order_imp(global_importance_values)
        if projection_required and len(global_importance_rank) > top_k:
            global_importance_rank = global_importance_rank[0:top_k]
        # sort the overall summary
        global_importance_values = global_importance_values[global_importance_rank]

    # TODO do we need to add names here as well?
    kwargs[ExplainParams.GLOBAL_IMPORTANCE_RANK] = global_importance_rank
    kwargs[ExplainParams.GLOBAL_IMPORTANCE_VALUES] = global_importance_values
    expected_values = None
    if isinstance(local_explanation, ExpectedValuesMixin):
        expected_values = local_explanation.expected_values
    scoring_model = None
    if isinstance(local_explanation, HasScoringModel):
        scoring_model = local_explanation.scoring_model
    if include_local:
        kwargs[ExplainParams.LOCAL_EXPLANATION] = local_explanation
    return create_global_explanation(expected_values=expected_values, classification=classification,
                                     scoring_model=scoring_model, **kwargs)
