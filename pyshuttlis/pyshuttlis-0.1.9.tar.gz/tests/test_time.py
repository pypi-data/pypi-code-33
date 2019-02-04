import pytest
from pytz import timezone
from datetime import datetime

from shuttlis.time import MilitaryTime, TimeDelta, WeekDay, TimezoneMismatch

IST_TIMEZONE = timezone("Asia/Kolkata")


def _mt_ist(time):
    return MilitaryTime(time, IST_TIMEZONE)


@pytest.mark.parametrize("hr,min", [(1, 20), (23, 59), (0, 0)])
def test_military_time_constructor(hr, min):
    mt = MilitaryTime.from_hr_min(hr, min, IST_TIMEZONE)
    assert hr == mt.hr
    assert min == mt.min
    assert IST_TIMEZONE.zone == mt.tz.zone


@pytest.mark.parametrize("hr,min", [(24, 00), (12, 61)])
def test_military_time_constructor_fails_when_hr_or_min_are_out_of_range(hr, min):
    with pytest.raises(AssertionError):
        MilitaryTime.from_hr_min(hr, min, IST_TIMEZONE)


@pytest.mark.parametrize(
    "mta,mtr",
    [
        (_mt_ist(1320) + TimeDelta(1, 20), _mt_ist(1440)),
        (_mt_ist(1320) + TimeDelta(0, 40), _mt_ist(1400)),
    ],
)
def test_military_time_add(mta, mtr):
    assert mtr == mta


@pytest.mark.parametrize(
    "mts,mtr",
    [
        (_mt_ist(1320) - TimeDelta(1, 20), _mt_ist(1200)),
        (_mt_ist(1320) - TimeDelta(0, 40), _mt_ist(1240)),
    ],
)
def test_military_time_sub(mts, mtr):
    assert mtr == mts


def test_military_time_inequality():
    assert _mt_ist(1000) != _mt_ist(900)


def test_weekday_eq():
    assert WeekDay.MONDAY == WeekDay.MONDAY


@pytest.mark.parametrize(
    "first,snd", [(WeekDay.MONDAY, WeekDay.TUESDAY), (WeekDay.MONDAY, WeekDay.SUNDAY)]
)
def test_weekday_lt(first, snd):
    assert first < snd


def test_weekday_extract_from_datetime():
    dt = datetime(year=2019, month=1, day=1)
    assert WeekDay.TUESDAY == WeekDay.extract_from_datetime(dt)


def test_weekday_extract_from_date():
    dt = datetime(year=2019, month=1, day=1)
    assert WeekDay.TUESDAY == WeekDay.extract_from_date(dt.date())


def test_military_time_with_timezone():
    assert _mt_ist(900) != MilitaryTime(900, timezone("America/Sao_Paulo"))


def test_military_time_sort():
    source_times = [_mt_ist(r) for r in range(2300, 1, -100)]
    assert sorted(source_times) == [_mt_ist(r) for r in range(100, 2400, 100)]


def test_military_time_compare_lt():
    assert _mt_ist(100) < _mt_ist(150)


def test_military_time_compare_gt():
    assert _mt_ist(1000) > _mt_ist(150)


def test_military_time_compare_gte():
    assert _mt_ist(150) >= _mt_ist(150)
    assert _mt_ist(1000) >= _mt_ist(150)


def test_military_time_compare_lte():
    assert _mt_ist(150) <= _mt_ist(150)
    assert _mt_ist(100) <= _mt_ist(150)


def test_military_time_compare_timezone_mismatch():
    with pytest.raises(TimezoneMismatch):
        _mt_ist(100) < MilitaryTime(100, timezone("America/Sao_Paulo"))


def test_weekday_str_conversion():
    assert str(WeekDay.SUNDAY) == "SUNDAY"


def test_time_delta_with_only_minutes():
    assert _mt_ist(1359) == _mt_ist(1300) + TimeDelta(min=59)


def test_hash_of_military_times():
    assert 2 == len({_mt_ist(900), _mt_ist(1000)})


def test_hash_of_same_military_time():
    assert 1 == len({_mt_ist(900), _mt_ist(900)})


def test_mt_in_list():
    assert _mt_ist(900) in [_mt_ist(900), _mt_ist(1000)]


def test_mt_not_in_list():
    assert _mt_ist(910) not in [_mt_ist(900), _mt_ist(1000)]
