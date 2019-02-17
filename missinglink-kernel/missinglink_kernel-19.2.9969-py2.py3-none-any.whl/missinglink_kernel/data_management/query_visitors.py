# -*- coding: utf8 -*-

from missinglink.legit.scam.luqum.tree import UnknownOperation, SearchField
from missinglink.legit.scam.luqum.utils import LuceneTreeTransformer
from missinglink.legit.scam import MLQueryVisitor, FunctionPhase


# noinspection PyClassicStyleClass
class SeedVisitor(MLQueryVisitor):
    def __init__(self):
        self.__seed = 1337

    @property
    def seed(self):
        return self.__seed

    def generic_visit(self, node, parents=None, context=None):
        pass

    def visit_function_seed(self, node, parents, context):
        self.__seed = node.seed


# noinspection PyClassicStyleClass
class SplitVisitor(MLQueryVisitor):
    def __init__(self):
        self.__split = {'train': 1.0}
        self.__split_field = None

    def has_phase(self, phase):
        return self.__split.get(phase) is not None

    def generic_visit(self, node, parents=None, context=None):
        pass

    def visit_function_split(self, node, parents, context):
        self.__split = node.split
        self.__split_field = node.split_field

    def get(self, phase):
        return self.__split.get(phase)


# noinspection PyClassicStyleClass
class DatapointVisitor(MLQueryVisitor):
    def __init__(self):
        self.datapoint = None

    def generic_visit(self, node, parents=None, context=None):
        pass

    def visit_function_datapoint_by(self, node, parents, context):
        self.datapoint = node.datapoint


# noinspection PyClassicStyleClass
class AddPhaseFunction(LuceneTreeTransformer):
    def __init__(self, phase):
        self.__phase_function = FunctionPhase.create_with_args(phase)
        self.__has_phase = False

    def visit_function_phase(self, node, parents, context):
        self.__has_phase = True
        return self.__phase_function

    def __call__(self, tree):
        result = self.visit(tree)
        if not self.__has_phase:
            result = UnknownOperation(self.__phase_function, result)

        return result
