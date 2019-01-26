# -*- coding: utf-8 -*-

from datetime import timedelta


def round_microseconds(date):
    fraction = date.microsecond / 1000000.0
    rounded = round(fraction, 0)

    if rounded >= 1:
        # round up by adding a second to the datetime
        date = date.replace(microsecond=0) + timedelta(seconds=1)

    return date
