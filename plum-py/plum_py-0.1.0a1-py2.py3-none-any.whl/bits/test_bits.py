# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from enum import IntEnum

import pytest
from baseline import Baseline

from plum import (
    ExcessMemoryError,
    InsufficientMemoryError,
    calcsize,
    getdump,
    pack,
    unpack,
)

from plum.bits import Bits, bitfield

from ..tests.utils import wrap_message


class MyEnum(IntEnum):

    A = 1
    B = 2


class MyBits(Bits, nbytes=2, fill=0x0):

    f1: int = bitfield(pos=0, size=8, default=0xab)
    f2: MyEnum = bitfield(pos=8, size=4)
    f3: bool = bitfield(pos=12, size=1)


m = MyBits(0xff)


class TestBasic(object):

    @staticmethod
    def test_init_default():
        i = MyBits()
        assert i == 0

    @staticmethod
    def test_init_int_extra_args():
        i = MyBits('100', base=16)
        assert i == 256

    @staticmethod
    def test_init_by_field():
        """Test initialization with individual fields."""
        expected = Baseline("""
            +---------+--------+----------+--------+--------+
            | Offset  | Access | Value    | Memory | Type   |
            +---------+--------+----------+--------+--------+
            | 0       | x      | 4608     | 00 12  | MyBits |
            |  [0:7]  |   .f1  | 0        |        | int    |
            |  [8:11] |   .f2  | MyEnum.B |        | MyEnum |
            |  [12]   |   .f3  | True     |        | bool   |
            +---------+--------+----------+--------+--------+
            """)

        m = MyBits(f1=0, f2=2, f3=1)

        assert getdump(m) == expected

    @staticmethod
    def test_init_by_field_with_defaults():
        """Test initialization with individual fields with some defaults."""
        expected = Baseline("""
            +---------+--------+----------+--------+--------+
            | Offset  | Access | Value    | Memory | Type   |
            +---------+--------+----------+--------+--------+
            | 0       | x      | 4779     | ab 12  | MyBits |
            |  [0:7]  |   .f1  | 171      |        | int    |
            |  [8:11] |   .f2  | MyEnum.B |        | MyEnum |
            |  [12]   |   .f3  | True     |        | bool   |
            +---------+--------+----------+--------+--------+
            """)

        m = MyBits(f2=2, f3=1)

        assert getdump(m) == expected

    @staticmethod
    def test_calcsize():
        assert calcsize(MyBits) == 2
        assert calcsize(MyBits(0)) == 2

    @staticmethod
    def test_dump():
        expected = Baseline("""
            +---------+--------+-------+--------+--------+
            | Offset  | Access | Value | Memory | Type   |
            +---------+--------+-------+--------+--------+
            | 0       | x      | 2561  | 01 0a  | MyBits |
            |  [0:7]  |   .f1  | 1     |        | int    |
            |  [8:11] |   .f2  | 10    |        | MyEnum |
            |  [12]   |   .f3  | False |        | bool   |
            +---------+--------+-------+--------+--------+
            """)

        assert getdump(MyBits(0xa01)) == expected

    @staticmethod
    def test_pack_instance():
        i = MyBits(0x0102)
        assert pack(i) == b'\x02\x01'

    @staticmethod
    def test_pack_builtins():
        assert pack(MyBits, 0x0102) == b'\x02\x01'

    @staticmethod
    def test_unpack():
        i = unpack(MyBits, b'\x02\x01')
        assert i == 0x0102

    @staticmethod
    def test_unpack_shortage():
        with pytest.raises(InsufficientMemoryError) as trap:
            unpack(MyBits, b'\x00')

        expected = Baseline("""


            +--------+--------+----------------------+--------+--------+
            | Offset | Access | Value                | Memory | Type   |
            +--------+--------+----------------------+--------+--------+
            | 0      | x      | <insufficient bytes> | 00     | MyBits |
            +--------+--------+----------------------+--------+--------+

            InsufficientMemoryError: 1 too few memory bytes to unpack MyBits (2
            needed, only 1 available), dump above shows interrupted progress
            """)

        assert wrap_message(trap.value) == expected

    @staticmethod
    def test_unpack_excess():
        with pytest.raises(ExcessMemoryError) as trap:
            unpack(MyBits, b'\x00\x01\x02')

        expected = Baseline("""


            +---------+--------+----------------+--------+--------+
            | Offset  | Access | Value          | Memory | Type   |
            +---------+--------+----------------+--------+--------+
            | 0       | x      | 256            | 00 01  | MyBits |
            |  [0:7]  |   .f1  | 0              |        | int    |
            |  [8:11] |   .f2  | MyEnum.A       |        | MyEnum |
            |  [12]   |   .f3  | False          |        | bool   |
            | 2       |        | <excess bytes> | 02     |        |
            +---------+--------+----------------+--------+--------+

            ExcessMemoryError: 1 unconsumed memory bytes (3 available, 2
            consumed), dump above shows interrupted progress
            """)

        assert wrap_message(trap.value) == expected
