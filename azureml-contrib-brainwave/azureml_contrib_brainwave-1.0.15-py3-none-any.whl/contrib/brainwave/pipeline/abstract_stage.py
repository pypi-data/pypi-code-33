# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Abstract stage for pipeline."""
from abc import ABC, abstractmethod
import json


class AbstractStage(ABC):
    """Base class for deployment stages."""

    @abstractmethod
    def _write_data(self, base_path: str):
        """Write data to store in model definition.

        :param base_path:
        """
        raise NotImplementedError

    @abstractmethod
    def json_dict(self) -> dict:
        """Json dict for writing to model definition manifest."""
        raise NotImplementedError

    @classmethod
    def __subclasshook__(cls, C):
        """Abusing subclasshook for jsondict."""
        return True


class StageEncoder(json.JSONEncoder):
    """JSONEncoder for AbstractStage."""

    def default(self, obj):  # pylint: disable=E0202
        """Return dictionary to write."""
        if issubclass(obj, AbstractStage):
            return {k: v for k, v in obj.json_dict().items() if v is not None}
        return json.JSONEncoder.default(self, obj)
