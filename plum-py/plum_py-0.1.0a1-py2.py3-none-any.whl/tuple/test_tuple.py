import pytest
from baseline import Baseline

from .. import (
    ExcessMemoryError,
    InsufficientMemoryError,
    calcsize,
    getdump,
    pack,
    unpack,
)

from ..int.little import UInt16, UInt8
from ._tuple import Tuple

from ..tests.utils import wrap_message


class Seq(Tuple, types=(UInt8, UInt16)):
    pass


class TestBasic(object):

    @staticmethod
    def test_instantiate_default():
        expected_dump = Baseline("""
            +--------+--------+-------+--------+-------+
            | Offset | Access | Value | Memory | Type  |
            +--------+--------+-------+--------+-------+
            |        | x      |       |        | Tuple |
            +--------+--------+-------+--------+-------+
            """)
        s = Tuple()
        assert getdump(s) == expected_dump

    @staticmethod
    def test_instantiate():
        expected_dump = Baseline("""
            +--------+--------+-------+--------+--------+
            | Offset | Access | Value | Memory | Type   |
            +--------+--------+-------+--------+--------+
            |        | x      |       |        | Seq    |
            | 0      |   [0]  | 1     | 01     | UInt8  |
            | 1      |   [1]  | 2     | 02 00  | UInt16 |
            +--------+--------+-------+--------+--------+
            """)
        s = Seq((1, 2))
        assert s == (1, 2)
        assert type(s[0]) is UInt8
        assert type(s[1]) is UInt16
        assert len(s) == 2
        assert getdump(s) == expected_dump

    @staticmethod
    def test_calcsize():
        assert calcsize(Tuple) == 0
        assert calcsize(Seq) == 3
        assert calcsize(Tuple()) == 0
        assert calcsize(Seq((0, 0))) == 3

    @staticmethod
    def test_dump():
        expected = Baseline("""
            +--------+--------+-------+--------+--------+
            | Offset | Access | Value | Memory | Type   |
            +--------+--------+-------+--------+--------+
            |        | x      |       |        | Seq    |
            | 0      |   [0]  | 1     | 01     | UInt8  |
            | 1      |   [1]  | 515   | 03 02  | UInt16 |
            +--------+--------+-------+--------+--------+
            """)

        assert getdump(Seq((0x01, 0x0203))) == expected

    @staticmethod
    def test_pack_instance():
        s = Seq((1, 0x0203))
        assert pack(s) == b'\x01\x03\x02'

    @staticmethod
    def test_pack_builtins():
        assert pack(Seq, (1, 0x0203)) == b'\x01\x03\x02'

    @staticmethod
    def test_unpack():
        s = unpack(Seq, b'\x01\x03\x02')

        expected_dump = Baseline("""
            +--------+--------+-------+--------+--------+
            | Offset | Access | Value | Memory | Type   |
            +--------+--------+-------+--------+--------+
            |        | x      |       |        | Seq    |
            | 0      |   [0]  | 1     | 01     | UInt8  |
            | 1      |   [1]  | 515   | 03 02  | UInt16 |
            +--------+--------+-------+--------+--------+
            """)

        assert getdump(s) == expected_dump

    @staticmethod
    def test_unpack_shortage():
        with pytest.raises(InsufficientMemoryError) as trap:
            unpack(Seq, b'\x00\x01')

        expected = Baseline("""


            +--------+--------+----------------------+--------+--------+
            | Offset | Access | Value                | Memory | Type   |
            +--------+--------+----------------------+--------+--------+
            |        | x      |                      |        | Seq    |
            | 0      |   [0]  | 0                    | 00     | UInt8  |
            | 1      |   [1]  | <insufficient bytes> | 01     | UInt16 |
            +--------+--------+----------------------+--------+--------+

            InsufficientMemoryError: 1 too few memory bytes to unpack UInt16 (2
            needed, only 1 available), dump above shows interrupted progress
            """)

        assert wrap_message(trap.value) == expected

    @staticmethod
    def test_unpack_excess():
        with pytest.raises(ExcessMemoryError) as trap:
            unpack(Seq, b'\x00\x01\x02\0x03')

        expected = Baseline("""


            +--------+--------+----------------+-------------+--------+
            | Offset | Access | Value          | Memory      | Type   |
            +--------+--------+----------------+-------------+--------+
            |        | x      |                |             | Seq    |
            | 0      |   [0]  | 0              | 00          | UInt8  |
            | 1      |   [1]  | 513            | 01 02       | UInt16 |
            | 3      |        | <excess bytes> | 00 78 30 33 |        |
            +--------+--------+----------------+-------------+--------+

            ExcessMemoryError: 4 unconsumed memory bytes (7 available, 3
            consumed), dump above shows interrupted progress
            """)

        assert wrap_message(trap.value) == expected

    @staticmethod
    def test_index():
        s = Seq((1, 0x0203))
        assert s[0] == 1
        assert s[1] == 0x0203
        assert len(s) == 2
        assert s[0:2] == (1, 0x0203)
