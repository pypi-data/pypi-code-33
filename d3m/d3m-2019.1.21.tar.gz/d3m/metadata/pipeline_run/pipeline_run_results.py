import typing

from d3m import container, exceptions
from d3m.metadata import problem as problem_module

from .predictions import Predictions
from .score import Score


class PipelineRunResults:
    def __init__(self) -> None:
        self.predictions: Predictions = Predictions()
        self.scores: typing.List[Score] = []

    def set_scores(
        self, scores: container.DataFrame, metrics: typing.Sequence[typing.Dict], problem_description: typing.Dict,
    ) -> None:
        self.scores = []
        for metric, targets, value in scores.itertuples(index=False, name=None):
            dataset_id, resolved_targets = self._resolve_targets(targets, problem_description)

            self.scores.append(Score(self._get_metric(metric, metrics), value, dataset_id, resolved_targets))

    def _get_metric(self, metric: problem_module.PerformanceMetric, performance_metrics: typing.Sequence[typing.Dict]) -> typing.Dict:
        """
        Returns a metric description from a list of them, given metric.

        Parameters
        ----------
        metric : PerformanceMetric
            A metric name.
        performance_metrics : Sequence[Dict]
            A list of performance metric descriptions used.

        Returns
        -------
        Dict
            A metric description.
        """

        for performance_metric in performance_metrics:
            if performance_metric['metric'] == metric:
                metric_description = {
                    'metric': performance_metric['metric'].name,
                }

                if performance_metric['params']:
                    metric_description['params'] = performance_metric['params']

                return metric_description

        raise KeyError("Cannot find metric '{metric}' among those defined in the problem description.".format(metric=metric))

    def _resolve_targets(self, target_names: str, problem_description: typing.Dict) -> typing.Tuple[str, typing.Sequence]:
        """
        Resolves a comma-separated list of target names into a list of target descriptions.

        Multiple targets are encoded comma-separated in scores DataFrame, so we expect
        ``target_names`` to be the same.

        We assume that all targets are from the same dataset and that there are not cross-dataset targets.

        Parameters
        ----------
        target_names : str
            A comma-separated list of target names.
        problem_description : Dict
            A problem description used for the pipeline run to set target columns.

        Returns
        -------
        Tuple[str, Sequence]
            A dataset ID to which targets belong and a list of dicts describing targets.
        """

        target_names_list = target_names.split(',')

        dataset_id = None
        targets = []
        for target_name in target_names_list:
            for problem_input in problem_description.get('inputs', []):
                for problem_target in problem_input.get('targets', []):
                    if problem_target['column_name'] == target_name:
                        if dataset_id is None:
                            dataset_id = problem_input['dataset_id']
                        elif dataset_id != problem_input['dataset_id']:
                            raise exceptions.NotSupportedError("Cross-dataset targets are not supported.")

                        targets.append(
                            {
                                'target_index': problem_target['target_index'],
                                'resource_id': problem_target['resource_id'],
                                'column_index': problem_target['column_index'],
                                'column_name': problem_target['column_name'],
                            },
                        )

        if len(target_names_list) != len(targets):
            raise exceptions.MismatchError("Expected targets do not match targets produced by the pipeline.")

        return dataset_id, targets

    def set_predictions(self, predictions: container.DataFrame) -> None:
        if not isinstance(predictions, container.DataFrame):
            return

        column_names = []
        for column_index in range(len(predictions.columns)):
            # We use column name from the DataFrame is metadata does not have it. This allows a bit more compatibility.
            column_names.append(predictions.metadata.query_column(column_index).get('name', predictions.columns[column_index]))

            self.predictions.add_values(predictions.iloc[:, column_index].tolist())

        self.predictions.add_headers(column_names)

    def to_json_structure(self) -> typing.Optional[typing.Dict[str, typing.Any]]:
        json_structure: typing.Dict[str, typing.Any] = {}

        predictions_json_structure = self.predictions.to_json_structure()
        if predictions_json_structure is not None:
            json_structure['predictions'] = predictions_json_structure

        scores_json_structure = self._scores_to_json_structure()
        if scores_json_structure is not None:
            json_structure['scores'] = scores_json_structure

        if json_structure:  # not empty
            return json_structure
        else:
            return None

    def _scores_to_json_structure(self) -> typing.Optional[typing.List]:
        json_structure = None

        for score in self.scores:
            score_json_structure = score.to_json_structure()
            if score_json_structure is not None:
                if json_structure is None:
                    json_structure = []
                json_structure.append(score_json_structure)

        return json_structure
