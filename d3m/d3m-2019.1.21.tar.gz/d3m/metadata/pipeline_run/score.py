import copy
import typing


class Score:
    def __init__(
        self, metric: typing.Dict, value: float, dataset_id: str, targets: typing.Sequence,
    ) -> None:
        self.metric = metric
        self.value = value
        self.dataset_id = dataset_id
        self.targets = targets

    def to_json_structure(self) -> typing.Dict:
        json_structure: typing.Dict[str, typing.Any] = {
            'metric': copy.deepcopy(self.metric),
            'value': self.value,
            'dataset_id': self.dataset_id,
            'targets': copy.deepcopy(self.targets),
        }

        return json_structure
