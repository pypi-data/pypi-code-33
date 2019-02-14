from calendar import monthrange
from datetime import timedelta


def monthdelta(d1, d2):
    '''
    Calculates the difference in months between two timepoints
    '''
    delta = 0
    while True:
        mdays = monthrange(d1.year, d1.month)[1]
        d1 += timedelta(days=mdays)
        if d1 <= d2:
            delta += 1
        else:
            break
    return delta


def calculate_passed_days(timestamp1, timestamp2):
    '''
    Calculates the number of days between two timestamps.
    '''
    if timestamp2 is None:
        return 0

    diff = timestamp1 - timestamp2
    min_sec = divmod(diff.days * 86400 + diff.seconds, 60)
    return min_sec[0] / (24 * 60)
