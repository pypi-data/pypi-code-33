from eggit.time_utils import DateTimeUtils
from datetime import datetime


def test_datetime_str_to_timestamp():
    datetime_str = '2018-01-01 00:00:00'
    assert DateTimeUtils.datetime_str_to_timestamp(datetime_str) == 1514736000
    assert DateTimeUtils.datetime_str_to_timestamp('Random String') is None


def test_get_datetime_object():
    datetime_str = '2018-01-01 00:00:00'
    assert DateTimeUtils.get_datetime_object(
        datetime_str) == datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    assert DateTimeUtils.get_datetime_object('Random String') is None


def test_get_datetime_string():
    datetime_str = '2018-01-01 00:00:00'
    datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    assert DateTimeUtils.get_datetime_string(datetime_obj) == datetime_str
    assert DateTimeUtils.get_datetime_string('not datetime object') is None


def test_now_str():
    now_str = DateTimeUtils.now_str()
    now_obj = DateTimeUtils.get_datetime_object(now_str)
    now = datetime.now()
    delta = now - now_obj
    assert delta.seconds == 0


def test_timestamp_to_datetime():
    timestamp = 1514736000
    timestamp2 = 1514736000000
    timestamp3 = '1514736000'
    timestamp4 = '1514736000000'
    timestamp5 = 1514736000.5
    timestamp6 = '1514736000.5'
    timestamp7 = 1514736000000.5
    timestamp8 = '1514736000000.5'
    assert DateTimeUtils.timestamp_to_datetime(timestamp) == datetime.fromtimestamp(timestamp)
    assert DateTimeUtils.timestamp_to_datetime(timestamp2) == datetime.fromtimestamp(timestamp)
    assert DateTimeUtils.timestamp_to_datetime(timestamp3) == datetime.fromtimestamp(timestamp)
    assert DateTimeUtils.timestamp_to_datetime(timestamp4) == datetime.fromtimestamp(timestamp)
    assert DateTimeUtils.timestamp_to_datetime(timestamp5) == datetime.fromtimestamp(timestamp5)
    assert DateTimeUtils.timestamp_to_datetime(timestamp6) == datetime.fromtimestamp(timestamp5)
    assert DateTimeUtils.timestamp_to_datetime(timestamp7) == datetime.fromtimestamp(timestamp7 / 1000)
    assert DateTimeUtils.timestamp_to_datetime(timestamp8) == datetime.fromtimestamp(timestamp7 / 1000)
    assert DateTimeUtils.timestamp_to_datetime(100) is None
    assert DateTimeUtils.timestamp_to_datetime('random string') is None
    assert DateTimeUtils.timestamp_to_datetime(object) is None


def test_timestamp_to_datetime_str():
    assert DateTimeUtils.timestamp_to_datetime_str(1514736000) == '2018-01-01 00:00:00'
