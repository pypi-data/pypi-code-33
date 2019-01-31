import time

HALF_DAY = 12 * 60 * 60

def format(epoch_time):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(epoch_time))
