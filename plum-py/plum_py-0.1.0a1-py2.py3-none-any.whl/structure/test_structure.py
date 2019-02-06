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
from plum.structure import Structure, member

from ..tests.utils import wrap_message


class Custom(Structure):

    m1: UInt8
    m2: UInt16 = 0x9988


class TestBasic(object):

    @staticmethod
    def test_init_dict():
        """Test initialization via dict (no defaults)."""
        c = Custom(dict(m1=1, m2=2))

        expected_dump = Baseline("""
            +--------+--------+-------+--------+--------+
            | Offset | Access | Value | Memory | Type   |
            +--------+--------+-------+--------+--------+
            |        | x      |       |        | Custom |
            | 0      |   .m1  | 1     | 01     | UInt8  |
            | 1      |   .m2  | 2     | 02 00  | UInt16 |
            +--------+--------+-------+--------+--------+
            """)

        assert getdump(c) == expected_dump

    @staticmethod
    def test_init_dict_default():
        """Test initialization via dict (use defaults)."""
        c = Custom(dict(m1=1))

        expected_dump = Baseline("""
            +--------+--------+-------+--------+--------+
            | Offset | Access | Value | Memory | Type   |
            +--------+--------+-------+--------+--------+
            |        | x      |       |        | Custom |
            | 0      |   .m1  | 1     | 01     | UInt8  |
            | 1      |   .m2  | 39304 | 88 99  | UInt16 |
            +--------+--------+-------+--------+--------+
            """)

        assert getdump(c) == expected_dump

    @staticmethod
    def test_init_params():
        """Test initialization via parameters (no defaults)."""
        c = Custom(m1=1, m2=2)

        expected_dump = Baseline("""
            +--------+--------+-------+--------+--------+
            | Offset | Access | Value | Memory | Type   |
            +--------+--------+-------+--------+--------+
            |        | x      |       |        | Custom |
            | 0      |   .m1  | 1     | 01     | UInt8  |
            | 1      |   .m2  | 2     | 02 00  | UInt16 |
            +--------+--------+-------+--------+--------+
            """)

        assert getdump(c) == expected_dump

    @staticmethod
    def test_init_params_default():
        """Test initialization via parameters (use defaults)."""
        c = Custom(m1=1)

        expected_dump = Baseline("""
            +--------+--------+-------+--------+--------+
            | Offset | Access | Value | Memory | Type   |
            +--------+--------+-------+--------+--------+
            |        | x      |       |        | Custom |
            | 0      |   .m1  | 1     | 01     | UInt8  |
            | 1      |   .m2  | 39304 | 88 99  | UInt16 |
            +--------+--------+-------+--------+--------+
            """)

        assert getdump(c) == expected_dump

    @staticmethod
    def test_init_combination():
        """Test initialization via dict and parameters.

        Verify members applied from both, keyword params win
        in conflict.

        """
        c = Custom(dict(m1=0, m2=2), m1=1)

        expected_dump = Baseline("""
            +--------+--------+-------+--------+--------+
            | Offset | Access | Value | Memory | Type   |
            +--------+--------+-------+--------+--------+
            |        | x      |       |        | Custom |
            | 0      |   .m1  | 1     | 01     | UInt8  |
            | 1      |   .m2  | 2     | 02 00  | UInt16 |
            +--------+--------+-------+--------+--------+
            """)

        assert getdump(c) == expected_dump

    @staticmethod
    def test_calcsize():
        assert calcsize(Custom) == 3
        assert calcsize(Custom(m1=1, m2=2)) == 3

    @staticmethod
    def test_dump():
        expected_dump = Baseline("""
            +--------+--------+-------+--------+--------+
            | Offset | Access | Value | Memory | Type   |
            +--------+--------+-------+--------+--------+
            |        | x      |       |        | Custom |
            | 0      |   .m1  | 1     | 01     | UInt8  |
            | 1      |   .m2  | 2     | 02 00  | UInt16 |
            +--------+--------+-------+--------+--------+
            """)

        assert getdump(Custom(m1=1, m2=2)) == expected_dump

    @staticmethod
    def test_pack_instance():
        i = Custom(m1=1, m2=2)
        assert pack(i) == b'\x01\x02\x00'

    @staticmethod
    def test_pack_builtins():
        assert pack(Custom, {'m1': 1, 'm2': 2}) == b'\x01\x02\x00'

    @staticmethod
    def test_unpack():
        c = unpack(Custom, b'\x01\x02\x00')

        expected_dump = Baseline("""
            +--------+--------+-------+--------+--------+
            | Offset | Access | Value | Memory | Type   |
            +--------+--------+-------+--------+--------+
            |        | x      |       |        | Custom |
            | 0      |   .m1  | 1     | 01     | UInt8  |
            | 1      |   .m2  | 2     | 02 00  | UInt16 |
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
            | 0      |   .m1  | 1                    | 01     | UInt8  |
            | 1      |   .m2  | <insufficient bytes> | 02     | UInt16 |
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
            | 0      |   .m1  | 1              | 01     | UInt8  |
            | 1      |   .m2  | 2              | 02 00  | UInt16 |
            | 3      |        | <excess bytes> | 03     |        |
            +--------+--------+----------------+--------+--------+

            ExcessMemoryError: 1 unconsumed memory bytes (4 available, 3
            consumed), dump above shows interrupted progress
            """)

        assert wrap_message(trap.value) == expected


# TODO - test use of member()
