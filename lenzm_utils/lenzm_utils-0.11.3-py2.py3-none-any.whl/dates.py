"""date utils"""
import bisect
import calendar
from contextlib import suppress
from datetime import date, datetime, timedelta
from enum import IntEnum
from typing import Iterable, Optional, Tuple, Generator, overload

from collections_extended import setlist
from .comparable_mixin import ComparableSameClassMixin

from ._duration import parse_duration_iso  # noqa


class Day(IntEnum):
	MON = 0
	TUE = 1
	WED = 2
	THU = 3
	FRI = 4
	SAT = 5
	SUN = 6


WEEKENDS = (Day.SAT, Day.SUN)
WEEKDAYS = (Day.MON, Day.TUE, Day.WED, Day.THU, Day.FRI)


def week_start(
	d: date,
	starts_on: Day = Day.SUN,
	) -> date:
	"""Return the first day of the week for the passed date.

	Args:
		d: When to get the week start for.
		starts_on: The day of the week that the week starts on.

	Returns:
		A the first day of the week containing d.
	"""
	if isinstance(d, datetime):
		d = d.date()
	days = (d.weekday() + 7 - starts_on) % 7
	d -= timedelta(days=days)
	return d


def workday_diff(  # noqa no way to make this simpler
		start_date: datetime,
		end_date: datetime,
		holidays: Iterable[date] = None,
) -> float:
	"""Calculate the number of working days between two dates."""
	# assert isinstance(start_date, datetime)
	# assert isinstance(end_date, datetime)
	sorted_holidays = setlist(sorted(holidays or []))
	if end_date < start_date:
		return -workday_diff(end_date, start_date, holidays=sorted_holidays)
	elif end_date == start_date:
		return 0
	# first full day is inclusive
	first_full_day = (start_date + timedelta(days=1)).date()
	# last full day is exclusive
	last_full_day = end_date.date()
	if last_full_day > first_full_day:
		num_full_days = (last_full_day - first_full_day) / timedelta(days=1)
		full_weeks, extra_days = divmod(num_full_days, 7)
		full_weeks = int(full_weeks)
		extra_days = int(extra_days)
		num_full_days -= full_weeks * len(WEEKENDS)
		# subtract out any working days that fall in the 'shortened week'
		for d in range(extra_days):
			if (first_full_day + timedelta(d)).weekday() in WEEKENDS:
				num_full_days -= 1
		# subtract out any holidays
		start_index = bisect.bisect_left(sorted_holidays, first_full_day)
		stop_index = bisect.bisect_right(sorted_holidays, last_full_day)
		for holiday in sorted_holidays[start_index:stop_index]:
			if holiday.weekday() not in WEEKENDS:
				num_full_days -= 1
	else:
		num_full_days = 0

	# Calculate partial days
	def should_exclude_day(d: date) -> bool:
		return d.weekday() in WEEKENDS or d in sorted_holidays

	partial_days = 0.0
	if end_date.date() == start_date.date():
		if not should_exclude_day(start_date):
			partial_days = (end_date - start_date) / timedelta(days=1)
	else:
		if not should_exclude_day(start_date):
			start_date_eod = midnight(first_full_day)
			partial_days += (start_date_eod - start_date) / timedelta(days=1)
		if not should_exclude_day(end_date):
			end_date_eod = midnight(last_full_day)
			partial_days += (end_date - end_date_eod) / timedelta(days=1)
	return partial_days + num_full_days


@overload
def midnight(d: None) -> None: ...  # noqa
@overload  # noqa
def midnight(d: date) -> datetime: ...  # noqa
def midnight(d):  # noqa
	"""Given a datetime.date, return a datetime.datetime of midnight."""
	if d is None:
		return None
	return datetime(d.year, d.month, d.day)


def past_complete_weeks(
	num_weeks: int,
	today: date = None,
	week_starts_on: Day = Day.SUN,
	) -> Tuple[date, date]:
	"""Return a tuple marking the beginning and end of the past number of weeks.

	Args:
		num_weeks: The number of weeks
		today: Date to use as today
		week_starts_on: What day starts the week
	Returns:
		beg (datetime), end (datetime)
	"""
	if today is None:
		today = date.today()
	end = week_start(today, starts_on=week_starts_on)
	num_days = 7 * num_weeks
	start = end - timedelta(days=num_days)
	return start, end


class Month(ComparableSameClassMixin):

	def __init__(self, year: int, month: int):
		if not 0 < month <= 12:
			raise ValueError('Invalid month')
		self.year = int(year)
		self.month = int(month)

	def first(self) -> date:
		"""Return a datetime.date object for the first of the month."""
		return self.date(1)

	def first_datetime(self) -> datetime:
		"""Return a datetime.date object for the first of the month."""
		return self.datetime(1)

	def first_string(self) -> str:
		return self.first().strftime('%m/%d/%Y')

	def mid(self) -> date:
		"""Return a datetime.date object for the 15th of the month."""
		return self.date(15)

	def mid_datetime(self) -> datetime:
		"""Return a datetime.date object for the 15th of the month."""
		return self.datetime(15)

	def mid_string(self) -> str:
		return self.mid().strftime('%m/%d/%Y')

	def last(self) -> date:
		return self.date(self.num_days())

	def num_days(self) -> int:
		return calendar.monthrange(self.year, self.month)[1]

	def date(self, day: int) -> date:
		"""Return a date for the day of the month.

		num can be a negative number to count back from the end of the month.
		eg. date(-1) is the last day of the month.
		"""
		if day < 0:
			day += self.num_days() + 1
		return date(self.year, self.month, day)

	def datetime(self, day: int, *args, **kwargs) -> datetime:
		return datetime(self.year, self.month, day, *args, **kwargs)

	def pace(self, d: datetime = None) -> float:
		"""Return how far through this month d is.

		If d isn't passed use datetime.now()
		"""
		if d is None:
			d = datetime.now()
		if self.month == d.month and self.year == d.year:
			days_into_month = (d - self.first_datetime()) / timedelta(days=1)
			return 1.0 - (days_into_month / self.num_days())
		elif self.year > d.year or (self.year == d.year and self.month > d.month):
			return 1.0
		else:
			return 0.0

	def next(self):
		if self.month == 12:
			return Month(self.year + 1, 1)
		else:
			return Month(self.year, self.month + 1)

	@classmethod
	def from_date(cls, d: Optional[date]):
		"""Create a Month from a date(time) object."""
		if not d:
			return None
		return cls(d.year, d.month)

	def _cmp_key(self):
		return self.year, self.month

	def __sub__(self, other):
		"""Return the number of months between two months."""
		return 12 * (self.year - other.year) + self.month - other.month

	@staticmethod
	def iter(start, end=None):
		"""Generate months between passed months.

		Args:
			start: The first month to yield.
			end: The final month to yield. If None, yield infinitely.

		Yields:
			Months between the passed values inclusive.
		"""
		month = start
		while end is None or month <= end:
			yield month
			month = month.next()

	def days(self) -> Generator[date, None, None]:
		"""Generate the dates in this month."""
		for i in range(self.num_days()):
			yield self.date(i + 1)


# Parsing

def parse_iso_date_with_colon(date_string: str) -> datetime:
	"""Parse a date in ISO format with a colon in the timezone.

	For example: 2014-05-01T15:08:00-07:00
	Or if the timezone is missing, parse that:
	For example: 2014-05-01T15:08:00
	"""
	with suppress(ValueError):
		return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S')
	with suppress(ValueError):
		return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%f')
	try:
		last_colon_index = date_string.rindex(':')
	except ValueError:
		raise ValueError(date_string)
	clean = date_string[:last_colon_index] + date_string[last_colon_index + 1:]
	return datetime.strptime(clean, '%Y-%m-%dT%H:%M:%S%z')


def parse_date_missing_zero_padding(
	date_string: str,
	sep: str = '/',
	order: str = 'mdy',
	min_year: int = 2000,
	) -> date:
	"""Parse dates without zero padding, e.g. 3/1/14.

	If min_year is set, then the year string can be two digits and is parsed as
	the year >= min_year with the last two digits as the passed year.

	Args:
		date_string: String to parse
		sep: The separator between month, day and year
		order: 'm', 'd' and 'y' indicating the order the month, day and year
		min_year: For two digit years, use the next year after min_year
	"""
	if len(order) != 3 or set(order) != set('mdy'):
		raise ValueError('Invalid order')
	strings = date_string.split(sep)
	if len(strings) != 3:
		raise ValueError('date_string does not contain 3 values')
	day = int(strings[order.index('d')])
	month = int(strings[order.index('m')])
	year = int(strings[order.index('y')])
	if year < min_year:
		if year < 0 or year >= 100:
			raise ValueError
		year = 100 * (min_year // 100) + year
		if year <= min_year:
			year += 100
	return date(year, month, day)
