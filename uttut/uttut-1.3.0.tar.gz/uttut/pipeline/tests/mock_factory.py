from typing import List

from ..ops.base import Operator, LabelAligner
from ..ops.factory import OperatorFactory


class MockLabelAligner(LabelAligner):

    def _transform(self, labels):
        return labels

    def _inverse_transform(self, labels):
        return labels


class MockStr2StrOp(Operator):

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        super().__init__(str, str)

    def __eq__(self, other):
        same_kwargs = self.kwargs == other.kwargs
        return same_kwargs and super().__eq__(other)

    def _transform(self, input_sequence: str):  # type: ignore
        return input_sequence, MockLabelAligner(
            edit={},
            input_sequence=input_sequence,
            output_length=len(input_sequence),
        )


class MockLst2LstOp(Operator):

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        super().__init__(list, list)

    def __eq__(self, other):
        same_kwargs = self.kwargs == other.kwargs
        return same_kwargs and super().__eq__(other)

    def _transform(self, input_sequence: List[str]):  # type: ignore
        return input_sequence, MockLabelAligner(
            edit={},
            input_sequence=input_sequence,
            output_length=len(input_sequence),
        )


class MockStr2LstOp(Operator):

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        super().__init__(str, list)

    def __eq__(self, other):
        same_kwargs = self.kwargs == other.kwargs
        return same_kwargs and super().__eq__(other)

    def _transform(self, input_sequence: str):  # type: ignore
        output_sequence = list(input_sequence)
        return output_sequence, MockLabelAligner(
            edit={},
            input_sequence=input_sequence,
            output_length=len(output_sequence),
        )


mock_factory = OperatorFactory()
mock_factory.register('Str2Str', MockStr2StrOp)
mock_factory.register('Lst2Lst', MockLst2LstOp)
mock_factory.register('Str2Lst', MockStr2LstOp)
