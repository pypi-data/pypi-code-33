import typing

from d3m.metadata import base as metadata_base

from .pipeline_run_step import PipelineRunStep
from .runtime_environment import RuntimeEnvironment


class PipelineRunSubpipelineStep(PipelineRunStep):
    def __init__(self, environment: RuntimeEnvironment = None) -> None:
        super().__init__(
            step_type=metadata_base.PipelineStepType.SUBPIPELINE,
            environment=environment,
        )
        self.steps: typing.List[typing.Dict] = []

    def to_json_structure(self) -> typing.Dict:
        json_structure = super().to_json_structure()
        json_structure.update({
            'steps': self.steps,
        })
        return json_structure

    def add_step(self, step: typing.Dict) -> None:
        self.steps.append(step)
