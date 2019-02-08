# coding: utf-8
import json
from operator import itemgetter

import pytest
from sqlalchemy import Table, Column, MetaData, create_engine, insert
from sqlalchemy.dialects.postgresql import JSONB

from pg_jsonb_flattener import JsonbTable
from .data import (
    array_of_objects, arrays_in_object, nested_arrays, nested_objects,
    simple_arrays, simple_object, simple_types)


# TODO: rendre ça plus configurable
DB_URL = 'postgresql://test:test@postgres:5432/test_pg_jsonb_flattener'
METADATA = MetaData()

ONE_JSON_FIELD_TABLE = Table(
    'one_json_field_table', METADATA,
    Column('field_one', JSONB)
)

TWO_JSON_FIELDS_TABLE = Table(
    'two_json_fields_table', METADATA,
    Column('field_one', JSONB),
    Column('field_two', JSONB)
)


@pytest.fixture(scope='session')
def engine():
    db_engine = create_engine(DB_URL)
    yield db_engine
    db_engine.dispose()


@pytest.fixture
def one_json_field_table(engine):
    ONE_JSON_FIELD_TABLE.create(engine)
    yield ONE_JSON_FIELD_TABLE
    ONE_JSON_FIELD_TABLE.drop(engine)


@pytest.fixture
def two_json_fields_table(engine):
    TWO_JSON_FIELDS_TABLE.create(engine)
    yield TWO_JSON_FIELDS_TABLE
    TWO_JSON_FIELDS_TABLE.drop(engine)


@pytest.mark.parametrize('data', [
    simple_types,
    simple_object,
    simple_arrays,
    array_of_objects,
    arrays_in_object,
    nested_arrays,
    nested_objects,
])
def test_parsing(data):
    schema = json.loads(data.schema)
    json_table = JsonbTable(ONE_JSON_FIELD_TABLE, field_one=schema)
    expected_columns = ['__'.join(['field_one', col])
                        for col in data.columns]
    assert sorted(
        [col.name for col in json_table.columns]
    ) == sorted(expected_columns)


@pytest.mark.parametrize('data', [
    simple_types,
    simple_object,
    simple_arrays,
    array_of_objects,
    arrays_in_object,
    nested_arrays,
    nested_objects,
])
def test_query_columns_one_json_field(engine, one_json_field_table, data):
    schema = json.loads(data.schema)
    json_table = JsonbTable(one_json_field_table, field_one=schema)

    with engine.connect() as conn:
        conn.execute(insert(one_json_field_table)
                     .values(field_one=data.json))

        result = conn.execute(json_table.get_query()).fetchone()

    expected_columns = ['__'.join(['field_one', col])
                        for col in data.columns]
    assert sorted(result.keys()) == sorted(expected_columns)


@pytest.mark.parametrize('data', [
    simple_types,
    simple_object,
    simple_arrays,
    array_of_objects,
    arrays_in_object,
    nested_arrays,
    nested_objects,
])
def test_query_columns_two_json_fields(engine, two_json_fields_table, data):
    schema = json.loads(data.schema)
    json_table = JsonbTable(
        two_json_fields_table, field_one=schema, field_two=schema)

    with engine.connect() as conn:
        conn.execute(insert(two_json_fields_table)
                     .values(field_one=data.json, field_two=data.json))

        result = conn.execute(json_table.get_query()).fetchone()

    expected_columns = (
        ['__'.join(['field_one', col]) for col in data.columns]
        + ['__'.join(['field_two', col]) for col in data.columns]
    )
    assert sorted(result.keys()) == sorted(expected_columns)


def test_simple_types_result(engine, one_json_field_table):
    data_module = simple_types
    schema = json.loads(data_module.schema)
    json_table = JsonbTable(one_json_field_table, field_one=schema)

    with engine.connect() as conn:
        conn.execute(insert(one_json_field_table)
                     .values(field_one=json.loads(data_module.json)))

        result = conn.execute(json_table.get_query()).fetchall()

    assert len(result) == 1
    assert result[0].field_one__integer == 42
    assert pytest.approx(3.141592, result[0].field_one__number)
    assert result[0].field_one__string == 'pouet'


def test_simple_object_result(engine, one_json_field_table):
    data_module = simple_object
    schema = json.loads(data_module.schema)
    json_table = JsonbTable(one_json_field_table, field_one=schema)

    with engine.connect() as conn:
        conn.execute(insert(one_json_field_table)
                     .values(field_one=json.loads(data_module.json)))

        result = conn.execute(json_table.get_query()).fetchall()

    assert len(result) == 1
    assert result[0].field_one__object__obj_int == 42
    assert pytest.approx(3.141592, result[0].field_one__object__obj_num)
    assert result[0].field_one__object__obj_str == 'pouet'


def test_simple_arrays_result(engine, one_json_field_table):
    data_module = simple_arrays
    schema = json.loads(data_module.schema)
    json_table = JsonbTable(one_json_field_table, field_one=schema)

    with engine.connect() as conn:
        conn.execute(insert(one_json_field_table)
                     .values(field_one=json.loads(data_module.json)))

        result = conn.execute(json_table.get_query()).fetchall()

    assert len(result) == 9

    ints = sorted([
        (r.field_one__int_arr__item, r.field_one__int_arr__item__index)
        for r in result if r.field_one__int_arr__item is not None
    ], key=itemgetter(1))
    assert ints == [(42, 1), (77, 2), (1664, 3)]

    nums = sorted([
        (r.field_one__num_arr__item, r.field_one__num_arr__item__index)
        for r in result if r.field_one__num_arr__item is not None
    ], key=itemgetter(1))
    assert pytest.approx(3.141592, nums[0][0])
    assert pytest.approx(1.618034, nums[1][0])
    assert pytest.approx(37.2, nums[2][0])

    strs = sorted([
        (r.field_one__str_arr__item, r.field_one__str_arr__item__index)
        for r in result if r.field_one__str_arr__item is not None
    ], key=itemgetter(1))
    assert strs == [(u'pouet', 1), (u'foo', 2), (u'bar', 3)]


def test_array_of_objects_result(engine, one_json_field_table):
    data_module = array_of_objects
    schema = json.loads(data_module.schema)
    json_table = JsonbTable(one_json_field_table, field_one=schema)

    with engine.connect() as conn:
        conn.execute(insert(one_json_field_table)
                     .values(field_one=json.loads(data_module.json)))

        result = conn.execute(json_table.get_query()).fetchall()

    assert len(result) == 2

    assert result[0].field_one__array__item__index == 1
    assert result[0].field_one__array__item__obj_int == 42
    assert pytest.approx(3.141592, result[0].field_one__array__item__obj_num)
    assert result[0].field_one__array__item__obj_str == 'pouet'

    assert result[1].field_one__array__item__index == 2
    assert result[1].field_one__array__item__obj_int == 77
    assert pytest.approx(1.618034, result[1].field_one__array__item__obj_num)
    assert result[1].field_one__array__item__obj_str == 'toto'


def test_arrays_in_object_result(engine, one_json_field_table):
    data_module = arrays_in_object
    schema = json.loads(data_module.schema)
    json_table = JsonbTable(one_json_field_table, field_one=schema)

    with engine.connect() as conn:
        conn.execute(insert(one_json_field_table)
                     .values(field_one=json.loads(data_module.json)))

        result = conn.execute(json_table.get_query()).fetchall()

    assert len(result) == 9

    ints = sorted([
        (r.field_one__object__int_arr__item,
         r.field_one__object__int_arr__item__index)
        for r in result if r.field_one__object__int_arr__item is not None
    ], key=itemgetter(1))
    assert ints == [(42, 1), (77, 2), (1664, 3)]

    nums = sorted([
        (r.field_one__object__num_arr__item,
         r.field_one__object__num_arr__item__index)
        for r in result if r.field_one__object__num_arr__item is not None
    ], key=itemgetter(1))
    assert pytest.approx(3.141592, nums[0][0])
    assert pytest.approx(1.618034, nums[1][0])
    assert pytest.approx(37.2, nums[2][0])

    strs = sorted([
        (r.field_one__object__str_arr__item,
         r.field_one__object__str_arr__item__index)
        for r in result if r.field_one__object__str_arr__item is not None
    ], key=itemgetter(1))
    assert strs == [(u'pouet', 1), (u'foo', 2), (u'bar', 3)]


def test_nested_arrays_result(engine, one_json_field_table):
    data_module = nested_arrays
    schema = json.loads(data_module.schema)
    json_table = JsonbTable(one_json_field_table, field_one=schema)

    with engine.connect() as conn:
        conn.execute(insert(one_json_field_table)
                     .values(field_one=json.loads(data_module.json)))

        result = conn.execute(json_table.get_query()).fetchall()

    assert len(result) == 4

    items = sorted([(r.field_one__nested_arrays__item__index,
                     r.field_one__nested_arrays__item__item__index,
                     r.field_one__nested_arrays__item__item)
                    for r in result])
    assert items == [(1, 1, 'abc'), (1, 2, 'def'),
                     (2, 1, 'tuw'), (2, 2, 'xyz')]


def test_nested_objects_result(engine, one_json_field_table):
    data_module = nested_objects
    schema = json.loads(data_module.schema)
    json_table = JsonbTable(one_json_field_table, field_one=schema)

    with engine.connect() as conn:
        conn.execute(insert(one_json_field_table)
                     .values(field_one=json.loads(data_module.json)))

        result = conn.execute(json_table.get_query()).fetchall()

    assert len(result) == 1

    assert result[0].field_one__object__nested__obj_int == 42
    assert pytest.approx(3.141592,
                         result[0].field_one__object__nested__obj_num)
    assert result[0].field_one__object__nested__obj_str == 'pouet'
