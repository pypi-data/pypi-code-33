"""
This file provides functionality for getting a random time within a specified range.
"""
from datetime import datetime
import random


def generate_random_timestamp(hours, minutes, seconds):
    """
    Generates a random timestamp in the range [00:00:00 - hours:minutes:seconds).

    :param hours: the hours component of the exclusive upper bound of the timestamp
    :param minutes: the minutes component of the exclusive upper bound of the timestamp
    :param seconds: the seconds component of the exclusive upper bound of the timestamp
    :return: a datetime containing the randomly generated timestamp in the hours, minutes, and seconds fields
    """
    random_hours = 0
    random_minutes = 0
    random_seconds = 0
    if hours > 0:
        random_hours = random.randint(0, hours)
        if random_hours == hours:
            random_minutes = random.randint(0, minutes)
            if random_minutes == minutes:
                random_seconds = random.randint(0, seconds)
            else:
                random_seconds = random.randint(0, 60)
        else:
            if random_minutes == minutes:
                random_seconds = random.randint(0, seconds)
            else:
                random_seconds = random.randint(0, 60)
    elif hours == 0 and minutes > 0:
        random_minutes = random.randint(0, minutes)
        if random_minutes == minutes:
            random_seconds = random.randint(0, seconds)
        else:
            random_seconds = random.randint(0, 60)
    elif hours == 0 and minutes == 0 and seconds > 0:
        random_seconds = random.randint(0, seconds)

    return datetime(hour=random_hours, minute=random_minutes, second=random_seconds)
