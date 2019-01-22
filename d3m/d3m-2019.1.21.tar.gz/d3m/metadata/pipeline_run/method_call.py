from datetime import datetime
import typing
import logging
import enum

from d3m import exceptions, types, utils
from d3m.primitive_interfaces.base import MultiCallResult, CallResult

from .runtime_environment import RuntimeEnvironment
from .status import Status

__all__ = ('MethodCall',)

INIT = '__init__'


class MethodCall:
    def __init__(
        self, method_name: str, *, runtime_arguments: typing.Dict = None,
        environment: RuntimeEnvironment = None
    ) -> None:
        if runtime_arguments is None:
            runtime_arguments = {}

        self.name = method_name
        self.runtime_arguments = runtime_arguments
        if self.name == INIT and self.runtime_arguments != {}:
            raise exceptions.InvalidArgumentValueError(
                f'MethodCall with method `{INIT}` cannot have arguments. '
                f'Hyper-parameters are the arguments to `{INIT}`.'
            )
        self.environment = environment
        self.status = Status()
        self.start: str = None
        self.end: str = None
        self.metadata: typing.Dict = None
        self.logging: typing.List[logging.LogRecord] = []

    def to_json_structure(self) -> typing.Dict:
        if self.start is None:
            raise exceptions.InvalidStateError('start timestamp not set')

        if self.end is None:
            raise exceptions.InvalidStateError('end timestamp not set')

        json_structure = {
            'name': self.name,
            'status': self.status.to_json_structure(),
            'start': self.start,
            'end': self.end,
        }

        if self.runtime_arguments != {}:
            json_structure['arguments'] = self._runtime_arguments_to_json_structure()

        if self.environment is not None:
            json_structure['environment'] = self.environment.to_json_structure()

        if not self._is_metadata_empty():
            json_structure['metadata'] = self.metadata

        if len(self.logging) > 0:
            json_structure['logging'] = self._logging_to_json_structure()

        return json_structure

    def _runtime_arguments_to_json_structure(self) -> typing.Dict:

        def recurse(item: typing.Any) -> typing.Any:
            if isinstance(item, enum.Enum):
                return item.name
            elif not isinstance(item, typing.Dict):
                return item
            else:
                json_structure = {}
                for key, value in item.items():
                    json_structure[key] = recurse(value)
                return json_structure

        return recurse(self.runtime_arguments)

    def set_start_timestamp(self) -> None:
        self.start = utils.datetime_for_json(datetime.now())

    def set_end_timestamp(self) -> None:
        self.end = utils.datetime_for_json(datetime.now())

    def set_successful(self, message: str = None) -> None:
        self.status.set_successful(message)

    def set_failed(self, message: str = None) -> None:
        self.status.set_failed(message)

    def set_result_metadata(self, result: typing.Union[CallResult, MultiCallResult]) -> None:
        if isinstance(result, CallResult):
            if result.value is not None and isinstance(result.value, types.Container):
                self.metadata = {
                    'value': self._get_metadata_json(result.value)
                }
        elif isinstance(result, MultiCallResult):
            self.metadata = {
                produce_method_name: self._get_metadata_json(value)
                for produce_method_name, value in result.values.items()
                if value is not None and isinstance(value, types.Container)
            }

    def _is_metadata_empty(self) -> bool:
        if self.metadata is None:
            return True
        for key, value in self.metadata.items():
            if value is not None:
                return False
        return True

    def _get_metadata_json(self, value: typing.Any) -> typing.List[typing.Dict]:
        return value.metadata.to_json_structure()

    def add_log_record(self, record: logging.LogRecord) -> None:
        self.logging.append(record)

    def _logging_to_json_structure(self) -> typing.List:
        json_structure = []
        for record in self.logging:
            json_structure.append(record)
        return json_structure
