import logging
from slither.slithir.operations.lvalue import OperationWithLValue
from slither.slithir.variables.tuple import TupleVariable

from slither.slithir.utils.utils import is_valid_lvalue, is_valid_rvalue

class Pack(OperationWithLValue):

    def __init__(self, tuple_var, values):
        assert isinstance(tuple_var, TupleVariable)
        super(Pack, self).__init__()
        self._lvalue = tuple_var
        self._values = values

    @property
    def read(self):
        return self._values

    @property
    def tuple(self):
        return self._lvalue


    def __str__(self):
        return "{}({})= PACK {}".format(self.lvalue,
                                        self.lvalue.type,
                                        self._values)
