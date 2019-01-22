import typing

from d3m.metadata import base as metadata_base

from .runtime_environment import RuntimeEnvironment
from .status import Status


class PipelineRunStep:
    def __init__(
        self, step_type: metadata_base.PipelineStepType, environment: RuntimeEnvironment = None
    ) -> None:
        self.type = step_type
        self.status: Status = Status()
        self.environment = environment

    def to_json_structure(self) -> typing.Dict:
        json_structure = {
            'type': self._type_to_json_structure(),
            'status': self.status.to_json_structure()
        }

        if self.environment is not None:
            json_structure['environment'] = self.environment.to_json_structure()

        return json_structure

    def _type_to_json_structure(self) -> str:
        return self.type.name

    def set_successful(self, message: str = None) -> None:
        self.status.set_successful(message)

    def set_failed(self, message: str = None) -> None:
        self.status.set_failed(message)
