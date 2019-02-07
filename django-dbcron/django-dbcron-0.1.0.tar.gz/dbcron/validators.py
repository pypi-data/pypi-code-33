from django.core import validators
from django.utils.translation import ugettext_lazy as _
from django.utils.deconstruct import deconstructible

MONTH_MAP = {
    'JAN': 1,
    'FEB': 2,
    'MAR': 3,
    'APR': 4,
    'MAY': 5,
    'JUN': 6,
    'JUL': 7,
    'AUG': 8,
    'SEP': 9,
    'OCT': 10,
    'NOV': 11,
    'DEC': 12,
}
DAYS = {
    'SUN': 0,
    'MON': 1,
    'TUE': 2,
    'WED': 3,
    'THU': 4,
    'FRI': 5,
    'SAT': 6,
}


@deconstructible
class BaseCrontabValidator:
    code = 'invalid'
    int_message = _("Enter a number between %d and %d.")
    range_message = _("Please enter valid range from %d and %s.")
    freq_message = _("Enter a valid positive number.")
    special_strings = []

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def validate_int(self, value, index):
        try:
            value = int(value)
        except TypeError:
            raise validators.ValidationError(
                message=self.int_message % (self.int_min, self.int_max),
                code=self.code
            )
        if not self.int_min <= value <= self.int_max:
            raise validators.ValidationError(
                message=self.int_message % (self.int_min, self.int_max),
                code=self.code
            )

    def validate_range(self, value, index):
        try:
            min_, max_ = value.split('-')
        except ValueError:
            raise validators.ValidationError(
                message=_("Bad range format"),
                code=self.code
            )
        self.validate_int(min_, index)
        self.validate_int(max_, index)
        min_, max_ = int(min_), int(max_)
        if min_ >= max_:
            raise validators.ValidationError(
                message=self.range_message % (self.int_min, self.int_max),
                code=self.code
            )

    def validate_frequency(self, value, index):
        star, freq = value.split('/')
        try:
            freq = int(freq)
        except TypeError:
            raise validators.ValidationError(message=self.freq_message,
                                             code=self.code)
        if freq <= 0:
            raise validators.ValidationError(message=self.freq_message,
                                             code=self.code)
        if star != '*':
            raise validators.ValidationError(
                message=_("The first character of frequency must be '*'."),
                code=self.code
            )

    def __call__(self, value):
        value = str(value)
        values = value.split(',')
        for i, value in enumerate(values):
            if value.isdigit():
                self.validate_int(value, i)
                continue
            elif value.startswith('-') and value[1:].isdigit():
                raise validators.ValidationError(
                    message=self.range_message % (self.int_min, self.int_max),
                    code=self.code
                )
            elif value.startswith('*/'):
                self.validate_frequency(value, i)
                continue
            elif '-' in value:
                self.validate_range(value, i)
                continue
            elif value.upper() in self.special_strings:
                continue
            elif value in ['*', '?']:
                continue
            raise validators.ValidationError(
                message=_("Enter a correct value."),
                code=self.code
            )


class SecondsValidator(BaseCrontabValidator):
    int_min = 0
    int_max = 59


class MinutesValidator(BaseCrontabValidator):
    int_min = 0
    int_max = 59


class HoursValidator(BaseCrontabValidator):
    int_min = 0
    int_max = 23


class DaysOfMonthValidator(BaseCrontabValidator):
    int_min = 1
    int_max = 31
    special_strings = ['L']


class MonthValidator(BaseCrontabValidator):
    int_min = 1
    int_max = 12
    month_list = MONTH_MAP
    special_strings = list(month_list)


class DaysOfWeekValidator(BaseCrontabValidator):
    int_min = 0
    int_max = 6
    day_list = DAYS
    special_strings = ['L'] + list(day_list)


class YearsValidator(BaseCrontabValidator):
    int_min = 1970
    int_max = 2099
