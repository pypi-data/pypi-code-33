import typing
import copy


class Predictions:
    def __init__(self) -> None:
        self.headers: typing.List[str] = []
        self.values: typing.List[typing.Any] = []

    def to_json_structure(self) -> typing.Optional[typing.Dict]:
        if len(self.headers) == 0 or len(self.values) == 0:
            return None
        else:
            return {
                'header': copy.deepcopy(self.headers),
                'values': copy.deepcopy(self.values)
            }

    def add_values(self, values: typing.Sequence) -> None:
        self.values.append(values)

    def add_headers(self, headers: typing.Sequence) -> None:
        self.headers += headers
