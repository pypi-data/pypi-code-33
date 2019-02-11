from django.test import TestCase
from django.core.validators import ValidationError
from dbcron import validators
from dbcron.tests import factories


class ValidatorTestMixin:
    def test_integer(self):
        value = factories.faker.random_int(self.validator.int_min,
                                           self.validator.int_max)
        self.validator()(value)

    def test_range(self):
        delta = self.validator.int_max - self.validator.int_min
        min_ = factories.faker.random_int(
            max([1, self.validator.int_min]),
            int(self.validator.int_min+delta/2)
        )
        max_ = factories.faker.random_int(min_+1, self.validator.int_max)
        value = '%d-%d' % (min_, max_)
        self.validator()(value)

    def test_list(self):
        values = [
            factories.faker.random_int(self.validator.int_min,
                                       self.validator.int_max)
            for i in range(3)
        ]
        value = ','.join([str(i) for i in values])
        self.validator()(value)

    def test_frequency(self):
        value = '*/%d' % factories.faker.random_int(
            max([1, self.validator.int_min]),
            self.validator.int_max
        )
        self.validator()(value)

    def test_star(self):
        value = '*'
        self.validator()(value)

    def test_ranges_in_list(self):
        values = []
        delta = self.validator.int_max - self.validator.int_min
        for i in range(3):
            min_ = factories.faker.random_int(
                max([1, self.validator.int_min]),
                int(self.validator.int_min+delta/2)
            )
            max_ = factories.faker.random_int(min_+1, self.validator.int_max)
            values.append('%d-%d' % (min_, max_))
        value = ','.join(values)
        self.validator()(value)

    def test_too_small_integer(self):
        value = self.validator.int_min - 1
        with self.assertRaises(ValidationError):
            self.validator()(value)

    def test_too_big_integer(self):
        value = self.validator.int_max + 1
        with self.assertRaises(ValidationError):
            self.validator()(value)

    def test_invalid_integer_in_list(self):
        values = []
        values.append(factories.faker.random_int(self.validator.int_min,
                                                 self.validator.int_max))
        values.append(self.validator.int_max + 1)
        value = ','.join([str(i) for i in values])
        with self.assertRaises(ValidationError):
            self.validator()(value)

    def test_invalid_frequency(self):
        value = '*/-1'
        with self.assertRaises(ValidationError):
            self.validator()(value)

    def test_invalid_string(self):
        value = factories.faker.first_name()
        with self.assertRaises(ValidationError):
            self.validator()(value)

    def test_invalid_range_format(self):
        values = [
            factories.faker.random_int(self.validator.int_min,
                                       self.validator.int_max)
            for i in range(3)
        ]
        value = '-'.join([str(i) for i in values])
        with self.assertRaises(ValidationError):
            self.validator()(value)


class SecondsValidatorTest(ValidatorTestMixin, TestCase):
    validator = validators.SecondsValidator


class MinutesValidatorTest(ValidatorTestMixin, TestCase):
    validator = validators.MinutesValidator


class HoursValidatorTest(ValidatorTestMixin, TestCase):
    validator = validators.HoursValidator


class DaysOfMonthValidatorTest(ValidatorTestMixin, TestCase):
    validator = validators.DaysOfMonthValidator

    def test_L(self):
        value = 'L'
        self.validator()(value)

    def test_interrogation_mark(self):
        value = '?'
        self.validator()(value)


class MonthValidatorTest(ValidatorTestMixin, TestCase):
    validator = validators.MonthValidator

    def test_string_month(self):
        value = factories.faker.random_element(self.validator.month_list)
        self.validator()(value)


class DaysOfWeekValidatorTest(ValidatorTestMixin, TestCase):
    validator = validators.DaysOfWeekValidator

    def test_L(self):
        value = 'L'
        self.validator()(value)

    def test_string_day(self):
        value = factories.faker.random_element(self.validator.day_list)
        self.validator()(value)

    def test_string_day_lower(self):
        value = factories.faker.random_element(self.validator.day_list).lower()
        self.validator()(value)

    def test_interrogation_mark(self):
        value = '?'
        self.validator()(value)


class YearsValidatorTest(ValidatorTestMixin, TestCase):
    validator = validators.YearsValidator
