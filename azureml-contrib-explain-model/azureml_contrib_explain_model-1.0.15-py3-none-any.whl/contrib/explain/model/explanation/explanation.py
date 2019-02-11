# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the explanations that are returned from explaining models."""

import os
import numpy as np

from azureml.core import Experiment, Run
from azureml._restclient.assets_client import AssetsClient
from azureml._restclient.constants import RUN_ORIGIN
from azureml.explain.model._internal.common import _sort_features, _sort_feature_list_multiclass, \
    _order_imp
from azureml.explain.model._internal.model_summary import ModelSummary
from azureml.explain.model._internal.results import _download_artifact, _create_download_dir
from azureml._logging import ChainedIdentity
from azureml.explain.model._internal.constants import Dynamic, ExplainParams, ExplanationParams, ExplainType, \
    History, BackCompat
from azureml.explain.model._internal.common import module_logger

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

    def __init__(self,
                 global_importance_values=None,
                 global_importance_rank=None,
                 global_importance_names=None,
                 **kwargs):
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
        if global_importance_names is not None:
            self._global_importance_names = global_importance_names
        elif self._features is not None:
            self._logger.debug('Features stored on explanation as strings')
            self._global_importance_names = _sort_features(self._features, global_importance_rank).tolist()
        else:
            # order of importance
            self._logger.debug('No features available, instead returning feature indices')
            self._global_importance_names = global_importance_rank.tolist()

    @property
    def global_importance_values(self):
        """Get the global feature importance values.

        :return: The model level feature importance values sorted in
            descending order.
        :rtype: list[float]
        """
        return self._global_importance_values

    @property
    def global_importance_names(self):
        """Get the sorted global feature importance names.

        :return: The feature names sorted by importance, or if names not provided, indices, same as rank.
        :rtype: Union[list[str], list[int]]
        """
        return self._global_importance_names

    @property
    def global_importance_rank(self):
        """Get the overall feature importance rank or indexes.

        For example, if original features are
        [f0, f1, f2, f3] and in global importance order they are [f2, f3, f0, f1], global_importance_rank
        would be [2, 3, 0, 1].

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

        For example, if original features are
        [f0, f1, f2, f3] and in per class importance order they are [[f2, f3, f0, f1], [f0, f2, f3, f1]],
        per_class_rank would be [[2, 3, 0, 1], [0, 2, 3, 1]].

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
    summary_object = ModelSummary()

    if explanation.features is not None:
        explanation._logger.debug('Uploading features as artifact')
        # upload features
        features = explanation.features if isinstance(explanation.features, list) else explanation.features.tolist()
        uploader._upload_artifact(upload_dir, History.FEATURES, features)
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

    if isinstance(explanation, LocalExplanation):
        explanation._logger.debug('Uploading local importance values')
        # upload local importance/shap value information
        uploader._upload_artifact(upload_dir, History.LOCAL_IMPORTANCE_VALUES, explanation.local_importance_values)
        local_values_artifact_info = [{
            History.PREFIX: os.path.normpath('{}/{}/{}/{}'.format(RUN_ORIGIN,
                                                                  run.id,
                                                                  upload_dir,
                                                                  History.LOCAL_IMPORTANCE_VALUES))
        }]
        local_values_metadata_info = {
            History.NAME: History.LOCAL_IMPORTANCE_VALUES
        }
        summary_object.add_from_get_model_summary(History.LOCAL_IMPORTANCE_VALUES,
                                                  (local_values_artifact_info, local_values_metadata_info))

    if isinstance(explanation, ExpectedValuesMixin) and explanation.expected_values is not None:
        explanation._logger.debug('Uploading expected values')
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
            explanation._logger.debug('Global explanation with features, uploading global names')
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
                explanation._logger.debug('Global classification explanation with features, uploading per class names')
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

        explanation._logger.debug('Uploading global rank and values')
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
            explanation._logger.debug('Classification explanation, so uploading per class rank and values')
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
        explanation._logger.debug('Class names are available, uploading them')
        # upload class information
        classes = explanation.classes
        if isinstance(classes, np.ndarray):
            classes = classes.tolist()
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


def download_model_explanation(run, top_k=None, **kwargs):
    """Get an explanation for a given run from run history.

    :param run: The run from which the explanation was generated
    :type run: azureml.core.run.Run
    :param top_k: If specified, limit the ordered data returned to the most important features and values
    :type top_k: int
    :return: The explanation as it was uploaded to run history
    :rtype: BaseExplanation
    """
    download_dir = _create_download_dir()
    assets_client = AssetsClient.create(run.experiment.workspace)
    explanation_assets = assets_client.get_assets_by_run_id_and_name(run.id, History.EXPLANATION_ASSET)

    # in case there's some issue with asset service, check
    if len(explanation_assets) > 0:
        module_logger.debug('Found at least one explanation asset, taking the first one')
        explanation_asset = explanation_assets[0]
    else:
        # if no asset, we can't do anything
        module_logger.debug('Did not find any explanation assets')
        return None

    # everything that might be available from the asset for construction an explanation
    local_importance_vals = None

    if (History.VERSION in explanation_asset.meta and
            explanation_asset.meta[History.VERSION] == History.EXPLANATION_ASSET_TYPE_V2):

        module_logger.debug('Explanation asset is version v2 or later')
        metadata_artifact_name = explanation_asset.meta[History.METADATA_ARTIFACT]
        storage_metadata = _download_artifact(run, download_dir, metadata_artifact_name)
        # classification and local importances are stored differently in v2 assets
        classification = explanation_asset.meta[ExplainType.MODEL] == ExplainType.CLASSIFICATION
        if History.LOCAL_IMPORTANCE_VALUES in storage_metadata:
            module_logger.debug('Downloading local importance values from v2')
            local_importance_vals = np.array(_download_artifact(run, download_dir, History.LOCAL_IMPORTANCE_VALUES))
        kwargs[ExplainParams.FEATURES] = _download_artifact(run, download_dir, History.FEATURES)
    else:
        # v1 asset backwards compatibility as of January 2019
        module_logger.debug('Explanation asset is v1 version')
        storage_metadata = _get_v2_metadata_from_v1(explanation_asset.meta)
        classification = History.PER_CLASS_VALUES in storage_metadata
        module_logger.debug('Downloading local importance values from v1')
        local_importance_vals = _download_artifact(run, download_dir, History.SHAP_VALUES)

    kwargs[ExplainParams.CLASSIFICATION] = classification
    if History.EXPECTED_VALUES in storage_metadata:
        module_logger.debug('Downloading expected values')
        kwargs[ExplainParams.EXPECTED_VALUES] = _download_artifact(run, download_dir, History.EXPECTED_VALUES)

    if local_importance_vals is not None:
        module_logger.debug('Creating local explanation')
        local_explanation = _create_local_explanation(local_importance_values=local_importance_vals, **kwargs)
        kwargs[ExplainParams.LOCAL_EXPLANATION] = local_explanation
        if History.GLOBAL_IMPORTANCE_VALUES not in storage_metadata:
            module_logger.debug('Global importance values not found, returning local explanation')
            return local_explanation

    # Include everything available on storage metadata
    if History.CLASSES in storage_metadata:
        module_logger.debug('Downloading class names')
        kwargs[ExplainParams.CLASSES] = _download_artifact(run, download_dir, History.CLASSES)
    if History.GLOBAL_IMPORTANCE_VALUES in storage_metadata:
        module_logger.debug('Downloading global importance values')
        kwargs[ExplainParams.GLOBAL_IMPORTANCE_VALUES] = \
            np.array(_download_sharded_data(run,
                                            download_dir,
                                            storage_metadata,
                                            History.GLOBAL_IMPORTANCE_VALUES,
                                            top_k=top_k))
    if History.GLOBAL_IMPORTANCE_RANK in storage_metadata:
        module_logger.debug('Downloading global importance ranks')
        kwargs[ExplainParams.GLOBAL_IMPORTANCE_RANK] = np.array(_download_sharded_data(run,
                                                                                       download_dir,
                                                                                       storage_metadata,
                                                                                       History.GLOBAL_IMPORTANCE_RANK,
                                                                                       top_k=top_k))
    if History.GLOBAL_IMPORTANCE_NAMES in storage_metadata:
        module_logger.debug('Downloading global importance names')
        kwargs[ExplainParams.GLOBAL_IMPORTANCE_NAMES] = \
            np.array(_download_sharded_data(run,
                                            download_dir,
                                            storage_metadata,
                                            History.GLOBAL_IMPORTANCE_NAMES,
                                            top_k=top_k))
    if History.PER_CLASS_NAMES in storage_metadata:
        module_logger.debug('Downloading per class names')
        kwargs[ExplainParams.PER_CLASS_NAMES] = np.array(_download_sharded_data(run,
                                                                                download_dir,
                                                                                storage_metadata,
                                                                                History.PER_CLASS_NAMES,
                                                                                top_k=top_k))
    # TODO does it make sense to return top k for rank?
    if History.PER_CLASS_RANK in storage_metadata:
        module_logger.debug('Downloading per class ranks')
        kwargs[ExplainParams.PER_CLASS_RANK] = np.array(_download_sharded_data(run,
                                                                               download_dir,
                                                                               storage_metadata,
                                                                               History.PER_CLASS_RANK,
                                                                               top_k=top_k))
    if History.PER_CLASS_VALUES in storage_metadata:
        module_logger.debug('Downloading per class values')
        kwargs[ExplainParams.PER_CLASS_VALUES] = np.array(_download_sharded_data(run,
                                                                                 download_dir,
                                                                                 storage_metadata,
                                                                                 History.PER_CLASS_VALUES,
                                                                                 top_k=top_k))

    return _create_global_explanation(**kwargs)


def download_model_explanation_from_run_id(workspace, experiment_name, run_id, top_k=None):
    """Get an explanation for a given run id from run history.

    :param workspace: An object that represents a workspace.
    :type workspace: azureml.core.workspace.Workspace
    :param experiment_name: The name of an experiment.
    :type experiment_name: str
    :param run_id: A GUID that represents a run.
    :type run_id: str
    :param top_k: If specified, limit the ordered data returned to the most important features and values
    :type top_k: int
    :return: The explanation as it was uploaded to run history
    :rtype: BaseExplanation
    """
    module_logger.debug('Constructing run from workspace, experiment, and run ID')
    experiment = Experiment(workspace, experiment_name)
    run = Run(experiment, run_id=run_id)
    return download_model_explanation(run, top_k=top_k)


def _download_sharded_data(run, download_dir, storage_metadata, name, top_k=None):
    """Download and aggregate a chunk of data from its sharded storage format.

    :param run: The run from which the explanation was generated
    :type run: azureml.core.run.Run
    :param download_dir: The directory to which the asset's files should be _download_sharded_data
    :type download_dir: str
    :param storage_metadata: The metadata dictionary for the asset's stored data
    :type storage_metadata: dict[str: dict[str: Union(str, int)]]
    :param name: The name/data type of the chunk to download_dir
    :type name: str
    :param top_k: If specified, limit the ordered data returned to the most important features and values
    :type top_k: int
    :return: The data chunk, anything from 1D to 3D, int or str
    """
    num_columns_to_return = int(storage_metadata[name][History.NUM_FEATURES])
    if top_k is not None:
        module_logger.debug('Top k is set, potentially reducing number of columns returned')
        num_columns_to_return = min(top_k, num_columns_to_return)
    num_blocks = int(storage_metadata[name][History.NUM_BLOCKS])
    if BackCompat.OLD_NAME in storage_metadata[name]:
        module_logger.debug('Working with constructed metadata from a v1 asset')
        # Backwards compatibility as of January 2019
        name = storage_metadata[name][BackCompat.OLD_NAME]
    full_data = np.array(_download_artifact(run, download_dir, name + '_0'))
    concat_dim = full_data.ndim - 1
    # Get the blocks
    for idx in range(1, num_blocks):
        block_name = '{}_{}'.format(name, str(idx))
        block = np.array(_download_artifact(run, download_dir, block_name))
        full_data = np.concatenate([full_data, block], axis=concat_dim)
        num_columns_read = full_data.shape[concat_dim]
        if num_columns_read >= num_columns_to_return:
            break
    full_data_list = full_data[..., :num_columns_to_return].tolist()
    return full_data_list


def _get_v2_metadata_from_v1(v1_metadata):
    """Convert the v1 asset metadata dict to a v2 asset metadata dict.

    :param v1_metadata: a flat dict of v1 metadata
    :type v1_metadta: dict[str: int]
    :return: a rich dict of v2 metadata
    :rtype: dict[str: dict[str: Union(str, int)]]
    """
    storage_metadata = {
        History.GLOBAL_IMPORTANCE_NAMES: _get_v2_shard_from_v1(v1_metadata,
                                                               BackCompat.OVERALL_FEATURE_ORDER,
                                                               History.GLOBAL_IMPORTANCE_NAMES),
        History.GLOBAL_IMPORTANCE_RANK: _get_v2_shard_from_v1(v1_metadata,
                                                              BackCompat.OVERALL_IMPORTANCE_ORDER,
                                                              History.GLOBAL_IMPORTANCE_RANK),
        History.GLOBAL_IMPORTANCE_VALUES: _get_v2_shard_from_v1(v1_metadata,
                                                                BackCompat.OVERALL_SUMMARY,
                                                                History.GLOBAL_IMPORTANCE_VALUES)
    }

    # these fields may or may not exist on v1 assets
    if History.BLOCK_SIZE + '_' + BackCompat.PER_CLASS_FEATURE_ORDER in v1_metadata:
        storage_metadata[History.PER_CLASS_NAMES] = \
            _get_v2_shard_from_v1(v1_metadata, BackCompat.PER_CLASS_FEATURE_ORDER, History.PER_CLASS_NAMES)
        storage_metadata[History.PER_CLASS_RANK] = \
            _get_v2_shard_from_v1(v1_metadata, BackCompat.PER_CLASS_IMPORTANCE_ORDER, History.PER_CLASS_RANK)
        storage_metadata[History.PER_CLASS_VALUES] = \
            _get_v2_shard_from_v1(v1_metadata, BackCompat.PER_CLASS_SUMMARY, History.PER_CLASS_VALUES)
    if History.NUM_CLASSES in v1_metadata:
        class_dict = {
            BackCompat.NAME: History.CLASSES,
            History.NUM_CLASSES: v1_metadata[History.NUM_CLASSES]
        }
        storage_metadata[History.CLASSES] = class_dict
    return storage_metadata


def _get_v2_shard_from_v1(v1_metadata, v1_name, v2_name):
    """Get specific metadata for v2 shards from v1 metadata.

    :param v1_metadata: a flat dict of v1 metadata
    :type v1_metadta: dict[str: int]
    :param v1_name: The v1 name for the chunked data
    :type v1_name: str
    :param v2_name: The v2 name for the chunked data
    :type v2_name: str
    :return: The dict of shard metadata
    :rtype: dict[str: str | int]
    """
    return {
        History.NAME: v2_name,
        BackCompat.OLD_NAME: v1_name,
        History.BLOCK_SIZE: v1_metadata[History.BLOCK_SIZE + '_' + v1_name],
        History.MAX_NUM_BLOCKS: v1_metadata[History.MAX_NUM_BLOCKS + '_' + v1_name],
        History.NUM_BLOCKS: v1_metadata[History.NUM_BLOCKS + '_' + v1_name],
        History.NUM_FEATURES: v1_metadata[History.NUM_FEATURES + '_' + v1_name]
    }


def _create_local_explanation(expected_values=None, classification=True,
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
    :return: The local explanation
    :rtype: LocalExplanation
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


def _create_global_explanation(local_explanation=None, expected_values=None,
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
    :return: The global explanation
    :rtype: GlobalExplanation
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


def _aggregate_global_from_local_explanation(local_explanation=None, include_local=True,
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
    return _create_global_explanation(expected_values=expected_values, classification=classification,
                                      scoring_model=scoring_model, **kwargs)
