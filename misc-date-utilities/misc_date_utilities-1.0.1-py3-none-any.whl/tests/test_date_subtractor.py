"""
This file contains some unit tests to test the date subtraction. They should account for most edge cases.
"""
import unittest
from date_difference import DateDifference

timezone = "America/Los_Angeles"


class TestDateSubtractionLogic(unittest.TestCase):

    def test_less_than_one_year(self):
        self.assertEqual(DateDifference.subtract_datestrings("2018-05-12 12:32", "2017-12-28 18:31", timezone),
                         "4 months, 13 days, 18 hours, and 1 minute")

    def test_negative_time(self):
        self.assertEqual(DateDifference.subtract_datestrings("2018-06-11 11:21", "2018-06-11 11:22", timezone),
                         "-1 minutes")

    def test_one_day(self):
        self.assertEqual(DateDifference.subtract_datestrings("2018-06-11 11:23", "2018-06-10 11:23", timezone),
                         "1 day")

    def test_slightly_less_than_one_day(self):
        self.assertEqual(DateDifference.subtract_datestrings("2018-06-11 11:22", "2018-06-10 11:23", timezone),
                         "23 hours and 59 minutes")

    def test_slightly_less_than_23_hours(self):
        self.assertEqual(DateDifference.subtract_datestrings("2018-06-11 11:22", "2018-06-10 12:23", timezone),
                         "22 hours and 59 minutes")

    def test_over_feburary(self):
        self.assertEqual(DateDifference.subtract_datestrings("2018-03-11 11:21", "2018-02-11 11:22", timezone),
                         "27 days, 23 hours, and 59 minutes")

    def test_one_month_after_feburary(self):
        self.assertEqual(DateDifference.subtract_datestrings("2018-03-11 11:22", "2018-02-11 11:22", timezone),
                         "1 month")

    def test_long_time(self):
        self.assertEqual(DateDifference.subtract_datestrings("2018-01-17 13:37", "1967-11-15 06:56", timezone),
                         "50 years, 2 months, 2 days, 6 hours, and 41 minutes")

    def test_difference_of_zero(self):
        self.assertEqual(DateDifference.subtract_datestrings("now", "now", timezone), "0 minutes")


if __name__ == "__main__":
    unittest.main()
