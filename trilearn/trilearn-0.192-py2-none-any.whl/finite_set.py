"""
Binary representation of a finite set.
"""

import bitstring

class FrozenFiniteSet:
    def __init__(self, n_elements):
        self.max_n_elements = n_elements
        self.ba = bitstring.Bits(n_elements)

    def issubset(self, t):
        pass

    def issuperset(self, t):
        return not self.issubset(t)

    def finite_set_from_int(self, max_elements, number):
        self.ba = bitstring.BitArray(max_elements)
        self.ba += bin(number)

    def copy(self, bs):
        b = FiniteSet()
        b.ba = self.ba.copy()
        return b

    def __sub__(self):
        # self.ba &= FULL & fs.ba.invert
        pass

    def __and__(self, fs):
        return self.ba & fs.ba

    def __or__(self, fs):
        return self.ba and fs.ba

    def __str__(self):
        list = []
        for i in range(self.max_n_elements):
            if self.ba[i]:
                list.append(i)
        return str(list)

    def __repr__(self):
        return self.ba.bin

    def __int__(self):
        return self.ba.int

    def __hash__(self):
        return int(self)


class FiniteSet:

    def __init__(self, n_elements):
        self.max_n_elements = n_elements
        self.ba = bitstring.BitArray(n_elements)

    def add(self, element):
        self.ba[element] = 1

    def remove(self, element):
        self.ba[element] = 0


    def union(sekf, t):
        pass

    def intersection(self, bs):
        pass

    def difference(self, bs):
        pass

    def symmetric_difference(self, bs):
        pass

#    def __add__(self, fs):
#        return self.ba | fs.ba

    def __iadd__(self, fs):
        self.ba |= fs.ba
        return self.ba

    def __iand__(self, fs):
        self.ba &= fs.ba
        return self.ba

