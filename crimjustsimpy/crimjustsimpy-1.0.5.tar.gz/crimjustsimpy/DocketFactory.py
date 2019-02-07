import collections.abc as abc
import typing as typ
import crimjustsimpy as cj
from crimjustsimpy import Case


class DocketFactory:
    """
    Factory to create dockets of cases based on the specified configuration items.
    """
    def __init__(self,*,case_factory:typ.Iterator[Case],arrival_gen:typ.Iterator[int]):
        assert isinstance(case_factory,abc.Iterator)
        assert isinstance(arrival_gen,abc.Iterator)
        self.case_factory = case_factory
        self.arrival_gen = arrival_gen
        self.id_gen = cj.IdGen()

    def __iter__(self):
        return self

    def __next__(self):
        docket = cj.Docket()
        docket.id = next(self.id_gen)

        # Select a random number of cases to arrive together.
        num_cases = next(self.arrival_gen)

        # Create the cases as configured.
        docket.fill(num_cases, self.case_factory)
        return docket



