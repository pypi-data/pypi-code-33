# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

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

from plum.int.little import UInt16, UInt8
from plum.sequence import Sequence

from ..tests.utils import wrap_message


class Custom(Sequence, types=(UInt8, UInt16)):
    pass


class TestBasic(object):

    @staticmethod
    def test_init_non_generator():
        """Test initialization via non-generator."""
        c = Custom((1, 2))

        expected_dump = Baseline("""
            +--------+--------+-------+--------+--------+
            | Offset | Access | Value | Memory | Type   |
            +--------+--------+-------+--------+--------+
            |        | x      |       |        | Custom |
            | 0      |   [0]  | 1     | 01     | UInt8  |
            | 1      |   [1]  | 2     | 02 00  | UInt16 |
            +--------+--------+-------+--------+--------+
            """)

        assert getdump(c) == expected_dump

    @staticmethod
    def test_init_generator():
        """Test initialization via generator."""
        c = Custom(range(1, 3))

        expected_dump = Baseline("""
            +--------+--------+-------+--------+--------+
            | Offset | Access | Value | Memory | Type   |
            +--------+--------+-------+--------+--------+
            |        | x      |       |        | Custom |
            | 0      |   [0]  | 1     | 01     | UInt8  |
            | 1      |   [1]  | 2     | 02 00  | UInt16 |
            +--------+--------+-------+--------+--------+
            """)

        assert getdump(c) == expected_dump

    @staticmethod
    def test_calcsize():
        assert calcsize(Custom) == 3
        assert calcsize(Custom((1, 3))) == 3

    @staticmethod
    def test_dump():
        expected_dump = Baseline("""
            +--------+--------+-------+--------+--------+
            | Offset | Access | Value | Memory | Type   |
            +--------+--------+-------+--------+--------+
            |        | x      |       |        | Custom |
            | 0      |   [0]  | 1     | 01     | UInt8  |
            | 1      |   [1]  | 2     | 02 00  | UInt16 |
            +--------+--------+-------+--------+--------+
            """)

        assert getdump(Custom((1, 2))) == expected_dump

    @staticmethod
    def test_pack_instance():
        i = Custom((1, 2))
        assert pack(i) == b'\x01\x02\x00'

    @staticmethod
    def test_pack_builtins():
        assert pack(Custom, (1, 2)) == b'\x01\x02\x00'

    @staticmethod
    def test_unpack():
        c = unpack(Custom, b'\x01\x02\x00')

        expected_dump = Baseline("""
            +--------+--------+-------+--------+--------+
            | Offset | Access | Value | Memory | Type   |
            +--------+--------+-------+--------+--------+
            |        | x      |       |        | Custom |
            | 0      |   [0]  | 1     | 01     | UInt8  |
            | 1      |   [1]  | 2     | 02 00  | UInt16 |
            +--------+--------+-------+--------+--------+
            """)

        assert getdump(c) == expected_dump

    @staticmethod
    def test_unpack_shortage():
        with pytest.raises(InsufficientMemoryError) as trap:
            unpack(Custom, b'\x01\x02')

        expected = Baseline("""


            +--------+--------+----------------------+--------+--------+
            | Offset | Access | Value                | Memory | Type   |
            +--------+--------+----------------------+--------+--------+
            |        | x      |                      |        | Custom |
            | 0      |   [0]  | 1                    | 01     | UInt8  |
            | 1      |   [1]  | <insufficient bytes> | 02     | UInt16 |
            +--------+--------+----------------------+--------+--------+

            InsufficientMemoryError: 1 too few memory bytes to unpack UInt16 (2
            needed, only 1 available), dump above shows interrupted progress
            """)

        assert wrap_message(trap.value) == expected

    @staticmethod
    def test_unpack_excess():
        with pytest.raises(ExcessMemoryError) as trap:
            unpack(Custom, b'\x01\x02\x00\x03')

        expected = Baseline("""


            +--------+--------+----------------+--------+--------+
            | Offset | Access | Value          | Memory | Type   |
            +--------+--------+----------------+--------+--------+
            |        | x      |                |        | Custom |
            | 0      |   [0]  | 1              | 01     | UInt8  |
            | 1      |   [1]  | 2              | 02 00  | UInt16 |
            | 3      |        | <excess bytes> | 03     |        |
            +--------+--------+----------------+--------+--------+

            ExcessMemoryError: 1 unconsumed memory bytes (4 available, 3
            consumed), dump above shows interrupted progress
            """)

        assert wrap_message(trap.value) == expected

    @staticmethod
    def test_repr():
        assert repr(Custom((1, 2))) == 'Custom([UInt8(1), UInt16(2)])'

    @staticmethod
    def test_str():
        assert str(Custom((1, 2))) == '[UInt8(1), UInt16(2)]'

