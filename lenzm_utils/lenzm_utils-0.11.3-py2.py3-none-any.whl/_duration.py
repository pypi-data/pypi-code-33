from datetime import timedelta
import string


DESIGNATORS_DAYS = {
	'Y': timedelta(days=365),
	'M': timedelta(days=30),
	'W': timedelta(days=7),
	'D': timedelta(days=1),
	}
DESIGNATORS_TIME = {
	'H': timedelta(hours=1),
	'M': timedelta(minutes=1),
	'S': timedelta(seconds=1),
	}
AMOUNT_CHARS = frozenset(string.digits + '.,')
DAYS_DESIGNATORS = 'YMWD'
TIME_DESIGNATORS = 'HMS'


def parse_duration_iso(s: str) -> timedelta:
	"""Parse an ISO 8601 duration string to a timedelta.

	This is inexact because years and months aren't specific amounts of time.

	PnYnMnDTnHnMnS where the 'n's are integer amounts.

	https://www.wikiwand.com/en/ISO_8601#/Durations

	Raises:
		ValueError: If the string is malformed.
	"""
	if not s.startswith('P'):
		raise ValueError('Duration string must start with a P')
	if len(s) < 3:
		raise ValueError('Duration string must be at least 3 characters long')
	if 'T' in s:
		days_string, time_string = s[1:].split('T')
	else:
		days_string, time_string = s[1:], ''
	running_total = _parse_duration_days(days_string, bool(time_string))
	running_total += _parse_duration_time(time_string)
	return running_total


def _parse_duration_days(days_string, any_time_string):
	running_total = timedelta(0)
	amount_string = ''
	last_designator = None
	for char in days_string:
		if char in AMOUNT_CHARS:
			amount_string += char
		else:
			if not amount_string:
				raise ValueError('Empty amount')
			# Is this the final value?
			if not any_time_string and char == days_string[-1]:
				amount = float(amount_string.replace(',', '.'))
			else:
				amount = int(amount_string)
			try:
				designator_value = DESIGNATORS_DAYS[char]
			except KeyError:
				raise ValueError('Unknown designator "%s"' % char)
			if last_designator:
				designator_index = DAYS_DESIGNATORS.index(char)
				last_designator_index = DAYS_DESIGNATORS.index(last_designator)
				if designator_index <= last_designator_index:
					raise ValueError(
						'Designators appear out of order, like minutes before '
						'hours'
						)
			running_total = running_total + (designator_value * amount)
			amount_string = ''
			last_designator = char
	return running_total


def _parse_duration_time(time_string):
	running_total = timedelta(0)
	amount_string = ''
	last_designator = None
	for char in time_string:
		if char in AMOUNT_CHARS:
			amount_string += char
		else:
			if not amount_string:
				raise ValueError('Empty amount')
			# Is this the final value?
			if char == time_string[-1]:
				amount = float(amount_string.replace(',', '.'))
			else:
				amount = int(amount_string)
			try:
				designator_value = DESIGNATORS_TIME[char]
			except KeyError:
				raise ValueError('Unknown designator "%s"' % char)
			if last_designator:
				designator_index = TIME_DESIGNATORS.index(char)
				last_designator_index = TIME_DESIGNATORS.index(last_designator)
				if designator_index <= last_designator_index:
					raise ValueError(
						'Designators appear out of order, like minutes before '
						'hours'
						)
			running_total = running_total + (designator_value * amount)
			amount_string = ''
			last_designator = char
	return running_total
