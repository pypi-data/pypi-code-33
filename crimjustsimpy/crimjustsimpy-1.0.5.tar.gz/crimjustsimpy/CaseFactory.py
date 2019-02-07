import collections.abc as abc
import typing as typ

import crimjustsimpy as cj


class CaseFactory():
    """
    Creates cases on demand, using the conviction probability generator.
    """

    def __init__(self, *, convict_gen: typ.Iterator[float]):
        assert isinstance(convict_gen, abc.Iterator)
        self.convict_gen = convict_gen
        self.id_gen = cj.IdGen()

    def __iter__(self):
        return self

    def __next__(self) -> cj.Case:
        return cj.Case(id=next(self.id_gen),prob_convict=next(self.convict_gen))
