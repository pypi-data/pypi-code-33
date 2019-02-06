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

from plum.int import Int
from plum.int.little import UInt16

from ..tests.utils import wrap_message


class TestBasic(object):

    @staticmethod
    def test_instantiate_default():
        i = UInt16()
        assert i == 0

    @staticmethod
    def test_instantiate_extra_args():
        i = UInt16('100', base=16)
        assert i == 256

    @staticmethod
    def test_calcsize():
        assert calcsize(UInt16) == 2
        assert calcsize(UInt16(0)) == 2

    @staticmethod
    def test_dump():
        expected = Baseline("""
            +--------+--------+-------+--------+--------+
            | Offset | Access | Value | Memory | Type   |
            +--------+--------+-------+--------+--------+
            | 0      | x      | 0     | 00 00  | UInt16 |
            +--------+--------+-------+--------+--------+
            """)

        assert getdump(UInt16(0)) == expected

    @staticmethod
    def test_pack_instance():
        i = UInt16(0x0102)
        assert pack(i) == b'\x02\x01'

    @staticmethod
    def test_pack_builtins():
        assert pack(UInt16, 0x0102) == b'\x02\x01'

    @staticmethod
    def test_unpack():
        i = unpack(UInt16, b'\x02\x01')
        assert i == 0x0102

    @staticmethod
    def test_unpack_shortage():
        with pytest.raises(InsufficientMemoryError) as trap:
            unpack(UInt16, b'\x00')

        expected = Baseline("""


            +--------+--------+----------------------+--------+--------+
            | Offset | Access | Value                | Memory | Type   |
            +--------+--------+----------------------+--------+--------+
            | 0      | x      | <insufficient bytes> | 00     | UInt16 |
            +--------+--------+----------------------+--------+--------+

            InsufficientMemoryError: 1 too few memory bytes to unpack UInt16 (2
            needed, only 1 available), dump above shows interrupted progress
            """)

        assert wrap_message(trap.value) == expected

    @staticmethod
    def test_unpack_excess():
        with pytest.raises(ExcessMemoryError) as trap:
            unpack(UInt16, b'\x00\x01\x02')

        expected = Baseline("""


            +--------+--------+----------------+--------+--------+
            | Offset | Access | Value          | Memory | Type   |
            +--------+--------+----------------+--------+--------+
            | 0      | x      | 256            | 00 01  | UInt16 |
            | 2      |        | <excess bytes> | 02     |        |
            +--------+--------+----------------+--------+--------+

            ExcessMemoryError: 1 unconsumed memory bytes (3 available, 2
            consumed), dump above shows interrupted progress
            """)

        assert wrap_message(trap.value) == expected


class Register(IntEnum):

    PC = 0
    SP = 1
    R0 = 2
    R1 = 3


class Register16(Int, nbytes=2, enum=Register):
    pass


class TestEnum:

    @staticmethod
    def test_str_valid_member():
        assert str(Register16(1)) == 'Register.SP'

    @staticmethod
    def test_str_invalid_member():
        assert str(Register16(99)) == '99'

    @staticmethod
    def test_repr_valid_member():
        assert repr(Register16(1)) == 'Register16(<Register.SP: 1>)'

    @staticmethod
    def test_repr_invalid_member():
        assert repr(Register16(99)) == 'Register16(99)'

    @staticmethod
    def test_dump_valid():
        expected_dump = Baseline("""
            +--------+--------+-------------+--------+------------+
            | Offset | Access | Value       | Memory | Type       |
            +--------+--------+-------------+--------+------------+
            | 0      | x      | Register.SP | 01 00  | Register16 |
            +--------+--------+-------------+--------+------------+
            """)

        assert getdump(Register16(1)) == expected_dump

    @staticmethod
    def test_dump_invalid():
        expected_dump = Baseline("""
            +--------+--------+-------+--------+------------+
            | Offset | Access | Value | Memory | Type       |
            +--------+--------+-------+--------+------------+
            | 0      | x      | 99    | 63 00  | Register16 |
            +--------+--------+-------+--------+------------+
            """)

        assert getdump(Register16(99)) == expected_dump
