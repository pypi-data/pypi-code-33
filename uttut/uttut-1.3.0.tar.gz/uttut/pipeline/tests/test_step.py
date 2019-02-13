import pytest

from ..ops.base import Operator
from ..step import Step


class MockedOperator(Operator):

    def __init__(self, state=None):
        super().__init__('in', 'out')
        self.state = state

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        same_state = self.state == other.state
        return same_state and super().__eq__(other)

    def _transform(self, input_sequence):
        pass


@pytest.fixture
def step():
    yield Step(MockedOperator())


def test_not_equal(step):
    assert step != Step(MockedOperator({'argg': '123'}))
    assert step != ()


def test_transform(step, mocker):
    mock_method = mocker.patch.object(step.op, 'transform')
    step.transform('abc')
    mock_method.assert_called_once_with(input_sequence='abc')


def test_attributes(step):
    assert MockedOperator().input_type == step.input_type
    assert MockedOperator().output_type == step.output_type
