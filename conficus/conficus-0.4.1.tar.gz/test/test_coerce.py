import sys
from datetime import datetime
from decimal import Decimal
import conficus
from conficus.parse import ConfigDict


if (sys.version_info.major < 3 and sys.version_info.minor < 4) \
        or sys.version_info.major == 2:
    from pathlib2 import Path
else:
    from pathlib import Path


def test_count_config_values(coerce_cfg):
    items = [i for i in coerce_cfg.walk_values()]
    assert len(items) == 41


def test_coerce_root_value(coerce_cfg):
    config = conficus._coerce(coerce_cfg)
    assert config['debug'] is True


def test_coerce_empty_values(coerce_cfg):
    config = conficus._coerce(coerce_cfg)
    assert config['empty-values.value1'] is None
    assert config['empty-values.value2'] is None
    assert config['empty-values.value3'] is None
    assert config['empty-values.value4'] is None


def test_coerce_numbers(coerce_cfg):
    config = conficus._coerce(coerce_cfg)

    assert type(config) == ConfigDict
    assert config['integer.value'] == 1
    assert config['float.value'] == 2.0

    config = conficus._coerce(coerce_cfg, decimal=True)
    assert config['float.value'] == Decimal(2)


def test_coerce_lists(coerce_cfg):
    config = conficus._coerce(coerce_cfg)

    assert config['empty-list.value'] == []
    assert config['single-line-list.integers'] == [1, 2, 3, 4]
    assert config['single-line-list.floats'] == [3.4, 3.4]
    assert config['single-line-list.strings'] == ['one', 'two', 'three']


def test_coerce_tuples(coerce_cfg):
    config = conficus._coerce(coerce_cfg)

    assert config['empty-tuple.value'] == tuple()
    assert config['single-line-tuple.integers'] == (1, 2, 3, 4)
    assert config['single-line-tuple.floats'] == (3.4, 3.4)
    assert config['single-line-tuple.strings'] == ('one', 'two', 'three')


def test_coerce_boolean(coerce_cfg):
    config = conficus._coerce(coerce_cfg)

    assert config['bool-true.val1'] is True
    assert config['bool-true.val2'] is True
    assert config['bool-true.val3'] is True
    assert config['bool-true.val4'] is True
    # assert config['bool-true.val5'] is True
    # assert config['bool-true.val6'] is True
    assert config['bool-true.val7'] is True
    assert config['bool-true.val8'] is True

    assert config['bool-false.val1'] is False
    assert config['bool-false.val2'] is False
    assert config['bool-false.val3'] is False
    assert config['bool-false.val4'] is False
    # assert config['bool-false.val5'] is False
    # assert config['bool-false.val6'] is False
    assert config['bool-false.val7'] is False


def test_coerce_datetime(coerce_cfg):
    config = conficus._coerce(coerce_cfg)

    assert isinstance(config['datetime.value'], datetime)
    assert config['datetime.value'].year == 2017
    assert config['datetime.value'].hour == 10


def test_coerce_date(coerce_cfg):
    config = conficus._coerce(coerce_cfg)

    assert isinstance(config['date.value'], datetime)
    assert config['date.value'].year == 2017
    assert config['date.value'].hour == 0


def test_coerce_string(coerce_cfg):
    config = conficus._coerce(coerce_cfg)

    assert isinstance(config['strings.str1'], str)
    assert config['strings.str1'] == 'unquoted string'
    assert config['strings.str2'] == ' a quoted string preserves white space '
    assert config['strings.str3'] == '23'
    assert config['strings.str4'] == 'Multi-quoted string.'
    assert config['strings.str5'] == 'This is a single line string.'
    assert config['strings.str6'] == 'This is a multiline\nstring.'
    assert config['strings.str7'] == 'This is a multiline\n   string with an\n   indent.'


def test_coerce_time(coerce_cfg):
    config = conficus._coerce(coerce_cfg)

    assert isinstance(config['time.value'], datetime)
    assert config['time.value'].year == 1900
    assert config['time.value'].hour == 10
    assert config['time.value'].minute == 15
    assert config['time.value'].second == 2


def test_coerce_path(coerce_cfg):
    config = conficus._coerce(coerce_cfg, pathlib=True)

    assert isinstance(config['path.windows1'], Path)
    assert isinstance(config['path.windows2'], Path) is False
    assert isinstance(config['path.windows3'], Path)
    assert isinstance(config['path.unix1'], Path)
    assert isinstance(config['path.unix2'], Path)


def test_coerce_multiline(multiline_cfg):
    config = conficus._coerce(multiline_cfg)

    assert len(config['multiline.list-of-strings']) == 4
    assert config['multiline.list-of-strings'][0] == 'Wonder Woman'

    assert isinstance(config['multiline.list-of-int'], list)
    assert len(config['multiline.list-of-int']) == 4
    assert isinstance(config['multiline.list-of-int'][0], int)

    assert isinstance(config['multiline.list-of-float'], list)
    assert len(config['multiline.list-of-float']) == 4
    assert isinstance(config['multiline.list-of-float'][0], float)

    assert isinstance(config['multiline.list-of-lists'], list)
    assert len(config['multiline.list-of-lists']) == 2
    assert isinstance(config['multiline.list-of-lists'][0], list)

    assert isinstance(config['multiline.tuple-of-strings'], tuple)
    assert len(config['multiline.tuple-of-strings']) == 4
    assert config['multiline.tuple-of-strings'][0] == 'Wonder Woman'

    assert isinstance(config['multiline.tuple-of-int'], tuple)
    assert len(config['multiline.tuple-of-int']) == 4
    assert isinstance(config['multiline.tuple-of-int'][0], int)

    assert len(config['multiline.text']) == 163
    assert isinstance(config['multiline.text'], str)
