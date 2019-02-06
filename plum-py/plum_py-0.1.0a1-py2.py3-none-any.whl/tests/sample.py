# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from plum import Memory, dump, getdump, pack, setvalue, unpack, view
from plum.int.little import UInt16, UInt8
from plum.structure import Structure, Varies, Member
from plum.bits import Bits, bitfield


class Custom(Bits, nbytes=4):

    m1: int = bitfield(pos=0, size=4)
    m2: int = bitfield(pos=4, size=4)


from enum import IntEnum
from plum.int import Int

class Register(IntEnum):

    PC = 0
    SP = 1
    R0 = 2
    R1 = 3


class Register16(Int, nbytes=2, enum=Register):
    pass

r = Register16(99)

# print(str(r))


class M2(Member):

    def get_cls(self, obj):
        if obj.m1 == 1:
            return UInt8
        else:
            return UInt16


class Custom(Structure):

    m1: UInt8

    m2: Varies = M2()

c = Custom(m1=1, m2=3)

# dump(c)

from plum.sequence import Sequence

class Custom(Sequence, types=(UInt8, UInt16)):
    pass

c = Custom((1, 2))

dump(c)

x = unpack(Custom, b'\x01\x02\x00')


from plum.array import Array

x = unpack(Array, b'\x01\x02\x00')


class MyArray(Array, dims=(2,3)):
    pass

x = unpack(MyArray, b'\x01\x02\x03\x04\x05\x06')
