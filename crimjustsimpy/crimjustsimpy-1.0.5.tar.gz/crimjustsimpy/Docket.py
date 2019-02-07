import collections.abc as abc
import typing as typ

from crimjustsimpy import Case


class Docket:
    """
    A list of cases handled as a group.
    """
    def __init__(self):
        self.cases = []
        self.id = None

    def fill(self, num_cases:int, case_factory:typ.Iterator[Case]):
        assert isinstance(case_factory, abc.Iterable)
        for i in range(num_cases):
            case = next(case_factory)
            case.docket = self
            self.cases.append(case)
