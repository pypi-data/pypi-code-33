from typing import List, Tuple
import warnings

from .base import Group
from .validation import (
    _validate_start_end,
    _validate_disjoint,
)


class Span:
    '''Integer offsets (start_i, end_i) of a sequence

    Args:
        start (int): start index (inclusive)
        end (int): end index (exclusive)
    '''

    def __init__(self, start: int, end: int):
        _validate_start_end(start, end)
        self.start, self.end = start, end

    def __eq__(self, other):
        if not isinstance(other, Span):
            return False
        same_start = other.start == self.start
        same_end = other.end == self.end
        return same_start and same_end

    def __str__(self):
        return f"({self.start}, {self.end})"

    def __repr__(self):
        return f"Span({self.start}, {self.end})"

    def __hash__(self):
        return hash(self.__str__())


class SpanGroup(Group):

    def __init__(self):
        self._spans = set()
        super().__init__()

    def add(self, start: int, end: int):  # type: ignore
        span = Span(start=start, end=end)
        self._spans.add(span)

    def done(self):
        if len(self._spans) == 0:
            self._spans = list(self._spans)
        else:
            self._spans = sorted(self._spans, key=lambda e: e.end)  # set -> list
            _validate_disjoint(self._spans)
            self._validate_contiguousness(self._spans)
        self._is_done = True

    def _validate_contiguousness(self, sorted_spans):
        if sorted_spans[0].start != 0:
            raise ValueError('Spans should start from 0')
        for idx in range(len(sorted_spans) - 1):
            if sorted_spans[idx].end != sorted_spans[idx + 1].start:
                raise ValueError('Spans should be contiguous.')

    @classmethod
    def add_all(cls, spans: List[Tuple[int, int]]):  # type: ignore
        span_group = cls()
        for span in spans:
            if len(span) == 2:
                start, end = span
                span_group.add(start, end)
            else:
                raise ValueError('Number of elements should = 2.')
        span_group.done()
        return span_group

    def is_empty(self):
        return len(self._spans) == 0

    def __eq__(self, other):
        self._warn_not_done()
        if not isinstance(other, SpanGroup):
            return False
        same_length = len(other) == len(self._spans)
        same_elements = set(other) == set(self._spans)
        return same_length and same_elements

    def __getitem__(self, value):
        if not self._is_done:
            raise RuntimeError('Please call `done` first.')
        return self._spans[value]

    def __len__(self):
        self._warn_not_done()
        return len(self._spans)

    def _warn_not_done(self):
        if not self._is_done:
            warnings.warn('SpanGroup needs validation, please call `done`.')

    def __repr__(self):
        return str(self.__class__.__name__)
