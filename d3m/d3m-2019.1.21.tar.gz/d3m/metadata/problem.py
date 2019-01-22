import json
import math
import os.path
import typing

from . import base
from d3m import exceptions, utils

__all__ = ('TaskType', 'TaskSubtype', 'PerformanceMetric', 'parse_problem_description')

# Comma because we unpack the list of validators returned from "load_schema_validators".
PROBLEM_SCHEMA_VALIDATOR, = utils.load_schema_validators(base.SCHEMAS, ('problem.json',))

PROBLEM_SCHEMA_VERSION = 'https://metadata.datadrivendiscovery.org/schemas/v0/problem.json'

D3M_SUPPORTED_VERSIONS = {'3.0', '3.1', '3.1.1', '3.1.2', '3.2.0'}


def sigmoid(x: float) -> float:
    """
    Numerically stable scaled logistic function.

    Maps all values ``x`` to [0, 1]. Values between -1000 and 1000 are
    mapped reasonably far from 0 and 1, after which the function
    converges to bounds.

    Parameters
    ----------
    x : float
        Input.

    Returns
    -------
    float
        Output.
    """

    scale = 1 / 1000

    if x >= 0:
        ex = math.exp(scale * -x)
        return 1 / (1 + ex)
    else:
        ex = math.exp(scale * x)
        return ex / (1 + ex)


class TaskTypeBase:
    @classmethod
    def get_map(cls) -> dict:
        """
        Returns the map between JSON string and enum values.

        Returns
        -------
        dict
            The map.
        """

        return {
            'classification': cls.CLASSIFICATION,  # type: ignore
            'regression': cls.REGRESSION,  # type: ignore
            'clustering': cls.CLUSTERING,  # type: ignore
            'linkPrediction': cls.LINK_PREDICTION,  # type: ignore
            'vertexNomination': cls.VERTEX_NOMINATION,  # type: ignore
            'communityDetection': cls.COMMUNITY_DETECTION,  # type: ignore
            'graphClustering': cls.GRAPH_CLUSTERING,  # type: ignore
            'graphMatching': cls.GRAPH_MATCHING,  # type: ignore
            'timeSeriesForecasting': cls.TIME_SERIES_FORECASTING,  # type: ignore
            'collaborativeFiltering': cls.COLLABORATIVE_FILTERING,  # type: ignore
            'objectDetection': cls.OBJECT_DETECTION,  # type: ignore
        }

    @classmethod
    def parse(cls, name: str) -> 'TaskTypeBase':
        """
        Converts JSON string into enum value.

        Parameters
        ----------
        name : str
            JSON string.

        Returns
        -------
        TaskType
            Enum value.
        """

        return cls.get_map()[name]

    def unparse(self) -> str:
        """
        Converts enum value to JSON string.

        Returns
        -------
        str
            JSON string.
        """

        for key, value in self.get_map().items():
            if self == value:
                return key

        raise exceptions.InvalidStateError("Cannot convert {self}.".format(self=self))


TaskType = utils.create_enum_from_json_schema_enum(
    'TaskType', base.DEFINITIONS_JSON,
    'definitions.problem.properties.task_type.oneOf[*].enum[*]',
    module=__name__, base_class=TaskTypeBase,
)


class TaskSubtypeBase:
    @classmethod
    def get_map(cls) -> dict:
        """
        Returns the map between JSON string and enum values.

        Returns
        -------
        dict
            The map.
        """

        return {
            None: cls.NONE,  # type: ignore
            'binary': cls.BINARY,  # type: ignore
            'multiClass': cls.MULTICLASS,  # type: ignore
            'multiLabel': cls.MULTILABEL,  # type: ignore
            'univariate': cls.UNIVARIATE,  # type: ignore
            'multivariate': cls.MULTIVARIATE,  # type: ignore
            'overlapping': cls.OVERLAPPING,  # type: ignore
            'nonOverlapping': cls.NONOVERLAPPING,  # type: ignore
        }

    @classmethod
    def parse(cls, name: str) -> 'TaskSubtypeBase':
        """
        Converts JSON string into enum value.

        Parameters
        ----------
        name : str
            JSON string.

        Returns
        -------
        TaskSubtype
            Enum value.
        """

        return cls.get_map()[name]

    def unparse(self) -> str:
        """
        Converts enum value to JSON string.

        Returns
        -------
        str
            JSON string.
        """

        for key, value in self.get_map().items():
            if self == value:
                return key

        raise exceptions.InvalidStateError("Cannot convert {self}.".format(self=self))


TaskSubtype = utils.create_enum_from_json_schema_enum(
    'TaskSubtype', base.DEFINITIONS_JSON,
    'definitions.problem.properties.task_subtype.oneOf[*].enum[*]',
    module=__name__, base_class=TaskSubtypeBase,
)


class PerformanceMetricBase:
    @classmethod
    def get_map(cls) -> dict:
        """
        Returns the map between JSON string and enum values.

        Returns
        -------
        dict
            The map.
        """

        return {
            'accuracy': cls.ACCURACY,  # type: ignore
            'precision': cls.PRECISION,  # type: ignore
            'recall': cls.RECALL,  # type: ignore
            'f1': cls.F1,  # type: ignore
            'f1Micro': cls.F1_MICRO,  # type: ignore
            'f1Macro': cls.F1_MACRO,  # type: ignore
            'rocAuc': cls.ROC_AUC,  # type: ignore
            'rocAucMicro': cls.ROC_AUC_MICRO,  # type: ignore
            'rocAucMacro': cls.ROC_AUC_MACRO,  # type: ignore
            'meanSquaredError': cls.MEAN_SQUARED_ERROR,  # type: ignore
            'rootMeanSquaredError': cls.ROOT_MEAN_SQUARED_ERROR,  # type: ignore
            'rootMeanSquaredErrorAvg': cls.ROOT_MEAN_SQUARED_ERROR_AVG,  # type: ignore
            'meanAbsoluteError': cls.MEAN_ABSOLUTE_ERROR,  # type: ignore
            'rSquared': cls.R_SQUARED,  # type: ignore
            'normalizedMutualInformation': cls.NORMALIZED_MUTUAL_INFORMATION,  # type: ignore
            'jaccardSimilarityScore': cls.JACCARD_SIMILARITY_SCORE,  # type: ignore
            'precisionAtTopK': cls.PRECISION_AT_TOP_K,  # type: ignore
            'objectDetectionAP': cls.OBJECT_DETECTION_AVERAGE_PRECISION,  # type: ignore
        }

    @classmethod
    def parse(cls, name: str) -> 'PerformanceMetricBase':
        """
        Converts JSON string into enum value.

        Parameters
        ----------
        name : str
            JSON string.

        Returns
        -------
        PerformanceMetric
            Enum value.
        """

        return cls.get_map()[name]

    def unparse(self) -> str:
        """
        Converts enum value to JSON string.

        Returns
        -------
        str
            JSON string.
        """

        for key, value in self.get_map().items():
            if self == value:
                return key

        raise exceptions.InvalidStateError("Cannot convert {self}.".format(self=self))

    def applicability_to_targets(self) -> bool:
        """
        Returns ``True`` if this metric is computed over all targets and not per target.

        Based on the return value one should pass or just a column with one target
        predictions (when ``False``) or a table with predictions for all targets (when ``True``)
        to the metric function for its ``y_true`` and ``y_pred`` arguments.

        Returns
        -------
        bool
            ``True`` if the metric applies to the set of all the target predictions.
        """

        return self in {self.ROOT_MEAN_SQUARED_ERROR_AVG}  # type: ignore

    def best_value(self) -> float:
        """
        The best possible value of the metric.

        Returns
        -------
        float
            The best possible value of the metric.
        """

        return {
            self.ACCURACY: 1.0,  # type: ignore
            self.PRECISION: 1.0,  # type: ignore
            self.RECALL: 1.0,  # type: ignore
            self.F1: 1.0,  # type: ignore
            self.F1_MICRO: 1.0,  # type: ignore
            self.F1_MACRO: 1.0,  # type: ignore
            self.ROC_AUC: 1.0,  # type: ignore
            self.ROC_AUC_MICRO: 1.0,  # type: ignore
            self.ROC_AUC_MACRO: 1.0,  # type: ignore
            self.MEAN_SQUARED_ERROR: 0.0,  # type: ignore
            self.ROOT_MEAN_SQUARED_ERROR: 0.0,  # type: ignore
            self.ROOT_MEAN_SQUARED_ERROR_AVG: 0.0,  # type: ignore
            self.MEAN_ABSOLUTE_ERROR: 0.0,  # type: ignore
            self.R_SQUARED: 1.0,  # type: ignore
            self.NORMALIZED_MUTUAL_INFORMATION: 1.0,  # type: ignore
            self.JACCARD_SIMILARITY_SCORE: 1.0,  # type: ignore
            self.PRECISION_AT_TOP_K: 1.0,  # type: ignore
            self.OBJECT_DETECTION_AVERAGE_PRECISION: 1.0,  # type: ignore
        }[self]

    def worst_value(self) -> float:
        """
        The worst possible value of the metric.

        Returns
        -------
        float
            The worst possible value of the metric.
        """

        return {
            self.ACCURACY: 0.0,  # type: ignore
            self.PRECISION: 0.0,  # type: ignore
            self.RECALL: 0.0,  # type: ignore
            self.F1: 0.0,  # type: ignore
            self.F1_MICRO: 0.0,  # type: ignore
            self.F1_MACRO: 0.0,  # type: ignore
            self.ROC_AUC: 0.0,  # type: ignore
            self.ROC_AUC_MICRO: 0.0,  # type: ignore
            self.ROC_AUC_MACRO: 0.0,  # type: ignore
            self.MEAN_SQUARED_ERROR: float('inf'),  # type: ignore
            self.ROOT_MEAN_SQUARED_ERROR: float('inf'),  # type: ignore
            self.ROOT_MEAN_SQUARED_ERROR_AVG: float('inf'),  # type: ignore
            self.MEAN_ABSOLUTE_ERROR: float('inf'),  # type: ignore
            self.R_SQUARED: float('-inf'),  # type: ignore
            self.NORMALIZED_MUTUAL_INFORMATION: 0.0,  # type: ignore
            self.JACCARD_SIMILARITY_SCORE: 0.0,  # type: ignore
            self.PRECISION_AT_TOP_K: 0.0,  # type: ignore
            self.OBJECT_DETECTION_AVERAGE_PRECISION: 0.0,  # type: ignore
        }[self]

    def normalize(self, value: float) -> float:
        """
        Normalize the ``value`` for this metric so that it is between 0 and 1,
        inclusive, where 1 is the best score and 0 is the worst.

        Parameters
        ----------
        value : float
            Value of this metric to normalize.

        Returns
        -------
        float
            A normalized metric.
        """

        worst_value = self.worst_value()
        best_value = self.best_value()

        return self._normalize(worst_value, best_value, value)

    @classmethod
    def _normalize(cls, worst_value: float, best_value: float, value: float) -> float:
        assert worst_value <= value <= best_value or worst_value >= value >= best_value, (worst_value, value, best_value)

        if math.isinf(best_value) and math.isinf(worst_value):
            value = sigmoid(value)
            if best_value > worst_value:  # "best_value" == inf, "worst_value" == -inf
                best_value = 1.0
                worst_value = 0.0
            else:  # "best_value" == -inf, "worst_value" == inf
                best_value = 0.0
                worst_value = 1.0
        elif math.isinf(best_value):
            value = sigmoid(value - worst_value)
            if best_value > worst_value:  # "best_value" == inf
                best_value = 1.0
                worst_value = 0.5
            else:  # "best_value" == -inf
                best_value = 0.0
                worst_value = 0.5
        elif math.isinf(worst_value):
            value = sigmoid(best_value - value)
            if best_value > worst_value:  # "worst_value" == -inf
                best_value = 0.5
                worst_value = 1.0
            else:  # "worst_value" == inf
                best_value = 0.5
                worst_value = 0.0

        return (value - worst_value) / (best_value - worst_value)

    def get_function(self) -> typing.Callable[..., float]:
        """
        Returns a function suitable for computing this metric.

        Some functions get extra parameters which should be provided as keyword arguments.

        Returns
        -------
        function
            A function with (y_true, y_pred, **kwargs) signature, returning float.
        """

        # Importing here to prevent import cycle.
        from d3m import metrics

        if self not in metrics.functions_map:
            raise exceptions.NotSupportedError("Computing metric {metric} is not supported.".format(metric=self))

        return metrics.functions_map[self]  # type: ignore


PerformanceMetric = utils.create_enum_from_json_schema_enum(
    'PerformanceMetric', base.DEFINITIONS_JSON,
    'definitions.performance_metric.oneOf[*].properties.metric.enum[*]',
    module=__name__, base_class=PerformanceMetricBase,
)


def parse_problem_description(problem_doc_path: str) -> typing.Dict:
    """
    Parses problem description according to ``problem.json`` metadata schema.

    It parses constants to enums when suitable.

    Parameters
    ----------
    problem_doc_path : str
        File path to the problem description (``problemDoc.json``).

    Returns
    -------
    dict
        A parsed problem description.
    """

    with open(problem_doc_path, 'r') as problem_doc_file:
        problem_doc = json.load(problem_doc_file)

    if problem_doc.get('about', {}).get('problemSchemaVersion', None) not in D3M_SUPPORTED_VERSIONS:
        raise exceptions.NotSupportedVersionError("Only supporting problem descriptions whose schema version is among {versions}.".format(versions=D3M_SUPPORTED_VERSIONS))

    # To be compatible with problem descriptions which do not adhere to the schema and have only one entry for data.
    if not isinstance(problem_doc['inputs']['data'], list):
        problem_doc['inputs']['data'] = [problem_doc['inputs']['data']]

    performance_metrics = []
    for performance_metric in problem_doc['inputs']['performanceMetrics']:
        params = {}

        # A workaround, setting a default value.
        # See: https://gitlab.datadrivendiscovery.org/MIT-LL/d3m_data_supply/issues/138#note_9137
        if performance_metric['metric'] in ['f1', 'precision', 'recall']:
            params['pos_label'] = performance_metric.get('pos_label', '1')

        if 'pos_label' in performance_metric:
            params['pos_label'] = performance_metric['pos_label']

        if 'K' in performance_metric:
            params['k'] = performance_metric['K']

        performance_metrics.append({
            'metric': PerformanceMetric.parse(performance_metric['metric']),
            'params': params,
        })

    inputs = []
    for data in problem_doc['inputs']['data']:
        targets = []
        for target in data['targets']:
            targets.append({
                'target_index': target['targetIndex'],
                'resource_id': target['resID'],
                'column_index': target['colIndex'],
                'column_name': target['colName'],
            })

            if 'numClusters' in target:
                targets[-1]['clusters_number'] = target['numClusters']

        privileged_data_columns = []
        for privileged_data in data.get('privilegedData', []):
            privileged_data_columns.append({
                'privileged_data_index': privileged_data['privilegedDataIndex'],
                'resource_id': privileged_data['resID'],
                'column_index': privileged_data['colIndex'],
                'column_name': privileged_data['colName'],
            })

        problem_input = {
            'dataset_id': data['datasetID'],
        }

        if targets:
            problem_input['targets'] = targets

        if privileged_data_columns:
            problem_input['privileged_data'] = privileged_data_columns

        inputs.append(problem_input)

    problem_id = problem_doc['about']['problemID']
    # Handle a special case for SCORE dataset splits (those which have "targets.csv" file).
    # They are the same as TEST dataset splits, but we present them differently, so that
    # SCORE dataset splits have targets as part of data. Because of this we also update
    # corresponding problem ID.
    # See: https://gitlab.com/datadrivendiscovery/d3m/issues/176
    if os.path.exists(os.path.join(os.path.dirname(problem_doc_path), '..', 'targets.csv')) and problem_id.endswith('_TEST'):
        problem_id = problem_id[:-5] + '_SCORE'

    # Also update dataset references.
    for data in problem_doc.get('inputs', {}).get('data', []):
        if data['datasetID'].endswith('_TEST'):
            data['datasetID'] = data['datasetID'][:-5] + '_SCORE'

    # "dataSplits" are not exposed because it is unclear for what it would be used.
    # It is mostly interesting to know how train/test split was made for evaluation.
    # See: https://gitlab.datadrivendiscovery.org/MIT-LL/d3m_data_supply/issues/37
    #      https://gitlab.datadrivendiscovery.org/MIT-LL/d3m_data_supply/issues/42
    description = {
        'id': problem_id,
        # "problemVersion" is required by the schema, but we want to be compatible with problem
        # descriptions which do not adhere to the schema.
        'version': problem_doc['about'].get('problemVersion', '1.0'),
        'name': problem_doc['about']['problemName'],
        'schema': PROBLEM_SCHEMA_VERSION,
        'problem': {
            'task_type': TaskType.parse(problem_doc['about']['taskType']),
            'task_subtype': TaskSubtype.parse(problem_doc['about'].get('taskSubType', None)),
        },
        'outputs': {
            'predictions_file': problem_doc['expectedOutputs']['predictionsFile'],
        }
    }

    if performance_metrics:
        description['problem']['performance_metrics'] = performance_metrics  # type: ignore

    if problem_doc['about'].get('problemDescription', None):
        description['description'] = problem_doc['about']['problemDescription']  # type: ignore

    if inputs:
        description['inputs'] = inputs  # type: ignore

    if problem_doc['expectedOutputs'].get('scoresFile', None):
        description['outputs']['scores_file'] = problem_doc['expectedOutputs']['scoresFile']  # type: ignore

    if 'dataAugmentation' in problem_doc:
        description['data_augmentation'] = problem_doc['dataAugmentation']

    description['digest'] = utils.compute_digest(utils.to_json_structure(description))

    PROBLEM_SCHEMA_VALIDATOR.validate(description)

    return description


if __name__ == '__main__':
    import logging
    import pprint
    import sys

    logging.basicConfig()

    for problem_doc_path in sys.argv[1:]:
        try:
            pprint.pprint(parse_problem_description(problem_doc_path))
        except Exception as error:
            raise Exception("Unable to parse problem description: {problem_doc_path}".format(problem_doc_path=problem_doc_path)) from error
