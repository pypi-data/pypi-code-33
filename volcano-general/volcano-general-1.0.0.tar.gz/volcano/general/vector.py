#!/usr/bin/python3


class Vector:
    def __init__(self, start: int, end: int = None, size: int = None):
        assert isinstance(start, int), start
        assert end is not None or size is not None
        assert end is None or size is None

        self.s = start
        if end is not None:
            self.e = end
        else:
            self.e = start + size - 1

    def intersects(self, v) -> bool:
        return not (v.s > self.e or self.s > v.e)

    def __eq__(self, v) -> bool:
        return self.s == v.s and self.e == v.e

    def __ne__(self, v) -> bool:
        return self.s != v.s or self.e != v.e

    def contains(self, v) -> bool:
        return self.s <= v.s and self.e >= v.e

    def contains_value(self, v: int) -> bool:
        return self.s <= v <= self.e

    def size(self) -> int:
        return self.e - self.s + 1

    def intersection(self, v):
        s = self.s if self.s > v.s else v.s
        e = self.e if self.e < v.e else v.e

        return Vector(s, end=e)
