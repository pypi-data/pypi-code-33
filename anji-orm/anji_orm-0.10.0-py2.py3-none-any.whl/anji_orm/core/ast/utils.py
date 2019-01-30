__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.0"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ["Interval"]


class Interval:

    __slots__ = ('left_bound', 'right_bound', 'left_close', 'right_close')

    def __init__(
            self, left_bound, right_bound,
            left_close: bool = False, right_close: bool = False) -> None:
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.left_close = left_close
        self.right_close = right_close

    def contains_interval(self, other: 'Interval') -> bool:
        if self.left_bound > other.left_bound:
            return False
        if self.left_bound == other.left_bound and other.left_close and not self.left_close:
            return False
        if self.right_bound < other.right_bound:
            return False
        if self.right_bound == other.right_bound and other.right_close and not self.right_close:
            return False
        return True

    def clone(self) -> 'Interval':
        return Interval(
            self.left_bound,
            self.right_bound,
            left_close=self.left_close,
            right_close=self.right_close
        )

    @property
    def valid(self):
        if self.left_bound < self.right_bound:
            return True
        return self.left_bound == self.right_bound and self.left_close and self.right_close

    def __eq__(self, other) -> bool:
        if not isinstance(other, Interval):
            return False
        return self.left_bound == other.left_bound and self.right_bound == other.right_bound and self.left_close == other.left_close and self.right_close == other.right_close

    def __contains__(self, item) -> bool:
        return (
            ((self.left_bound < item) or (self.left_close and self.left_bound == item)) and
            ((self.right_bound > item) or (self.right_close and self.right_bound == item))
        )

    def __str__(self) -> str:
        return f"{'[' if self.left_close else '('}{self.left_bound}, {self.right_bound}{']' if self.right_close else ')'}"
