import collections
import time


def generate_test_data(number_entries=100, time_interval=30):
    end_time = time.time()
    data_set = collections.OrderedDict()
    for t in range(number_entries, 0, -1):
        t = t - 1
        curr_time = end_time - (t * time_interval)
        data_set[curr_time] = t
    return end_time, data_set
