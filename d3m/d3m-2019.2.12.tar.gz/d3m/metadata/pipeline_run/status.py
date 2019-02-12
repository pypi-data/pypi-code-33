import typing
from d3m.metadata import base as metadata_base
from d3m.exceptions import InvalidStateError

__all__ = ('Status')


class Status:
    def __init__(self) -> None:
        self._status_set = False
        self.state: typing.Optional[bool] = None
        self.message: typing.Optional[str] = None

    def set_successful(self, message: str = '') -> None:
        self.state = metadata_base.PipelineRunStatusState.SUCCESS.name
        self.message = message
        self._status_set = True

    def set_failed(self, message: str = '') -> None:
        self.state = metadata_base.PipelineRunStatusState.FAILURE.name
        self.message = message
        self._status_set = True

    def to_json_structure(self) -> typing.Dict[str, typing.Any]:
        if not self._status_set:
            raise InvalidStateError('status not set')
        json_structure: typing.Dict[str, typing.Any] = {
            'state': self.state,
        }
        if self.message is not None and self.message != '':
            json_structure['message'] = self.message
        return json_structure

    def is_failed(self) -> bool:
        return self.state == metadata_base.PipelineRunStatusState.FAILURE.name
