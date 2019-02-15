import logging

from slither.slithir.operations.lvalue import OperationWithLValue
from slither.core.variables.variable import Variable
from slither.slithir.variables import TupleVariable
from slither.core.declarations.function import Function
from slither.slithir.utils.utils import is_valid_lvalue, is_valid_rvalue

class TmpPhi(OperationWithLValue):

    def __init__(self, left_variable, nodes):
        assert isinstance(left_variable, str)
        assert isinstance(nodes, set)
        super(TmpPhi, self).__init__()
        self._lvalue = left_variable
        self._rvalues = nodes

    @property
    def read(self):
        return [self._rvalues]

    @property
    def rvalues(self):
        return self._rvalues

    def __str__(self):
        return '{} := \u03D5({})'.format(self.lvalue, [n.node_id for n in self._rvalues])
