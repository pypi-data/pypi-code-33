from typing import List
import warnings

from .base import Group
from .validation import (
    _validate_start_end,
    _validate_disjoint,
)


class Replacement:
    '''Represents an edit to a Sequence such as a string or a list

    A sequence is a collection of objects that can be indexed in a linear fashion. E.g. a string

    A `Replacement` stores the data for substitution of values in a sequence.
    It represents the replacing a continuous slice of the sequence with the items of `new_value`.
    (The semantics are similar to Python's built-in slice assignment feature
     https://docs.python.org/3/reference/simple_stmts.html#assignment-statements ,
     but more restrictive in that negative integers are not allowed for `start` and `end`.)


    E.g.
    The transformation from "" to "abc": Replacement(0, 0, "abc")
    The transformation from "abc" to "aBc": Replacement(1, 2, "B")
    The transformation from "aBc" to "aBcdef": Replacement(3, 3, "def")
    The transformation from "aBcdef" to "": Replacement(0, 6, "")
    Note that insertion at position i is represented as Replacement(i, i, ...)
    ("Insertion at i" means that the original i-th element is moved to the right;
     similar to Python's list.insert)

    Args:
        start (int): start index (inclusive)
        end (int): end index (exclusive)
        new_value (obj): the new subsequence
        annotation (str, optional): an annotation for this replacement
    '''

    def __init__(
            self,
            start: int,
            end: int,
            new_value,
            annotation: str = None,
        ):
        _validate_start_end(start, end)
        self.start, self.end = start, end
        self.new_value = new_value
        self.annotation = annotation

    def __eq__(self, other):
        same_start = other.start == self.start
        same_end = other.end == self.end
        same_new_values = other.new_value == self.new_value
        return same_start and same_end and same_new_values

    def __str__(self):
        return f"({self.start}, {self.end}) => '{self.new_value}'"

    def __repr__(self):
        return f"Replacement({self.start}, {self.end}, " \
            f"{self.new_value}, annotation={self.annotation})"

    def __hash__(self):
        return hash(self.__repr__())


class ReplacementGroup(Group):

    def __init__(self):
        self._replacements = set()
        super().__init__()

    def add(  # type: ignore
            self,
            start: int,
            end: int,
            new_value,
            annotation=None,
        ):
        replacement = Replacement(
            start=start,
            end=end,
            new_value=new_value,
            annotation=annotation,
        )
        self._replacements.add(replacement)

    def done(self):
        if len(self._replacements) == 0:
            self._replacements = list(self._replacements)
        else:
            self._validate_new_values()
            self._replacements = sorted(self._replacements, key=lambda e: e.end)  # set -> list
            self._replacements = sorted(self._replacements, key=lambda e: e.start)
            _validate_disjoint(self._replacements)
        self._is_done = True

    def _validate_new_values(self):
        target_type = type(list(self._replacements)[0].new_value)
        for i, rep in enumerate(self._replacements):
            if not isinstance(rep.new_value, target_type):
                raise TypeError(
                    f"the new_value of {i}-th element is not a(an) {target_type.__name__}")

    @classmethod
    def add_all(cls, replacements: List[tuple]) -> 'ReplacementGroup':  # type: ignore
        '''
        replacements = [
            (
                start: int,
                end: int,
                new_value: str or tokens,
                annotation: str, # optional
            ),
            ...
        ]
        '''
        replacement_group = cls()
        for replacement in replacements:
            replacement_group.add(*replacement)
        replacement_group.done()
        return replacement_group

    def is_empty(self):
        return len(self._replacements) == 0

    def __eq__(self, other):
        self._warn_not_done()
        if not isinstance(other, ReplacementGroup):
            return False
        same_length = len(other) == len(self._replacements)
        same_elements = set(other) == set(self._replacements)
        return same_length and same_elements

    def __getitem__(self, value):
        if not self._is_done:
            raise RuntimeError('Please call `done` first.')
        return self._replacements[value]

    def __len__(self):
        self._warn_not_done()
        return len(self._replacements)

    def _warn_not_done(self):
        if not self._is_done:
            warnings.warn('ReplacementGroup needs validation, please call `done`.')

    def __repr__(self):
        n_elements = len(self._replacements)
        return f"ReplacementGroup has {n_elements} elements"
