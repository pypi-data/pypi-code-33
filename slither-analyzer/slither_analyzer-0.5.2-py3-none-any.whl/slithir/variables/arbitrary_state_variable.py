
from .variable import SlithIRVariable
from slither.core.variables.local_variable import LocalVariable
from slither.core.children.child_function import ChildFunction

"""
    Represent an arbitrary state variable
    Use when a function parameter is a storage reference
"""
class ArbitraryStateIRVariable(SlithIRVariable, ChildFunction):

    def __init__(self, local_variable, index):
        assert isinstance(local_variable, LocalVariable)

        super(ArbitraryStateIRVariable, self).__init__()

        # initiate ChildFunction
        self.set_function(local_variable.function)

        # initiate Variable
        self._name = local_variable.name
        self._initial_expression = None
        self._type = local_variable.type
        self._initialized = True
        self._visibility = None
        self._is_constant = False

        self._index = index

    @property
    def index(self):
        return self._index

    @property
    def ssa_name(self):
        return 'ref_{}_{}'.format(self._name, self.index)
