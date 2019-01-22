import typing
import uuid

from d3m import container
from d3m.metadata import base as metadata_base

from .pipeline_run_results import PipelineRunResults
from .pipeline_run_step import PipelineRunStep
from .status import Status


class Run:
    def __init__(self, phase: metadata_base.PipelineRunPhase) -> None:
        self.phase = phase
        self.fold_group_id: uuid.UUID = None
        self.fold: int = None
        self.data_preparation_pipeline: typing.Dict = None
        self.scoring_pipeline: typing.Dict = None
        self.results: PipelineRunResults = PipelineRunResults()

    def set_fold_group(self, fold_group_id: uuid.UUID, fold: int) -> None:
        self.fold_group_id = fold_group_id
        self.fold = fold

    def set_data_preparation_pipeline(self, pipeline: typing.Dict, steps: typing.List[PipelineRunStep], status: Status) -> None:
        self.data_preparation_pipeline = {
            'pipeline': pipeline,
            'steps': steps,
            'status': status,
        }

    def set_scoring_pipeline(self, pipeline: typing.Dict, steps: typing.List[PipelineRunStep], status: Status) -> None:
        self.scoring_pipeline = {
            'pipeline': pipeline,
            'steps': steps,
            'status': status,
        }

    def set_scores(
        self, scores: container.DataFrame, metrics: typing.Sequence[typing.Dict], problem_description: typing.Dict,
    ) -> None:
        self.results.set_scores(scores, metrics, problem_description)

    def set_predictions(self, predictions: container.DataFrame) -> None:
        self.results.set_predictions(predictions)

    def to_json_structure(self) -> typing.Dict[str, typing.Any]:
        json_structure: typing.Dict[str, typing.Any] = {
            'phase': self._phase_to_json_structure()
        }

        if self.fold_group_id is not None and self.fold is not None:
            json_structure['fold_group'] = {
                'id': str(self.fold_group_id),
                'fold': self.fold
            }

        if self.data_preparation_pipeline is not None:
            json_structure['data_preparation'] = self._data_preparation_pipeline_to_json_structure()

        if self.scoring_pipeline is not None:
            json_structure['scoring'] = self._scoring_pipeline_to_json_structure()

        results_json_structure = self.results.to_json_structure()
        if results_json_structure is not None:
            json_structure['results'] = results_json_structure

        return json_structure

    def _data_preparation_pipeline_to_json_structure(self) -> typing.Dict[str, typing.Any]:
        return {
            'pipeline': self.data_preparation_pipeline['pipeline'],
            'steps': [step.to_json_structure() for step in self.data_preparation_pipeline['steps']],
            'status': self.data_preparation_pipeline['status'].to_json_structure(),
        }

    def _scoring_pipeline_to_json_structure(self) -> typing.Dict[str, typing.Any]:
        return {
            'pipeline': self.scoring_pipeline['pipeline'],
            'steps': [step.to_json_structure() for step in self.scoring_pipeline['steps']],
            'status': self.scoring_pipeline['status'].to_json_structure(),
        }

    def _phase_to_json_structure(self) -> str:
        return self.phase.name
