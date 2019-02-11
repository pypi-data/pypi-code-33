import pytest

from pgrsql2data.main import TableSchema


def test_placeholder():
    # TODO: I promise there'll be proper tests here soon ;-)
    table_schema = TableSchema()
    assert table_schema is not None
