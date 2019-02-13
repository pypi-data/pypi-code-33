from .ops.base import Operator


class Step:

    def __init__(self, op: Operator):
        self.op = op

    def __eq__(self, other):
        if not isinstance(other, Step):
            return False
        same_op = self.op == other.op
        return same_op

    @property
    def input_type(self):
        return self.op.input_type

    @property
    def output_type(self):
        return self.op.output_type

    def transform(self, input_sequence):
        return self.op.transform(input_sequence=input_sequence)
