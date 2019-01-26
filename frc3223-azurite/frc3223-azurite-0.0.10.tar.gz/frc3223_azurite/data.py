import csv
import numpy


def read_csv(fnom):
    """
    takes a csv file that consists of one header row and many data rows
    and reads it into a numpy array.

    :returns: dictionary mapping header text to column data
    """
    with open(fnom, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)
        
    data = numpy.genfromtxt(fnom, delimiter=',', skip_header=1)
    assert len(headers) == data.shape[1]
    results = {}
    for i, header in enumerate(headers):
        results[header] = data[:, i]

    return results


def show_data(fnom, 
        time_key="time", 
        time_delta_key=None,
        s_t=None, e_t=None,
        s=None, e=None, 
        value_keys=None, 
        exclude_value_keys=None,
        show_dt=True
        ):
    """
    given a csv file, readable by `read_csv`, of data sampled over time, 
    make plots of some or all data against time.

    time can either be specified as a time column, which must be a strictly
    increasing sequence of real numbers, or as a time delta column, which must 
    be a sequence of strictly positive real numbers.

    if there is a time column, `time_key` identifies it by the header value.

    if there is a time delta column, `time_delta_key` identifies it by the 
    header value, and `time_key` must not identify an existing column.

    if plotting data for all time is not desired, a range can be specified
    either as row indexes with parameters `s` and `e` or as times with 
    parameters `s_t` and `e_t`. mixing is supported, e.g. `s=20, e_t=10.5`, 
    but not `s=20, s_t=10.5`.

    if plotting data for all columns is not desired, a list of 
    columns to include can be specified with parameter `value_keys`, or a list
    of columns to exclude can be specified with parameter `exclude_value_keys`.

    the time delta between measurements will also be plotted vs time. this can
    be turned off with `show_dt=False`

    :param fnom: name of csv file, e.g. `"data.csv"`
    :param time_key: identifies the time column.
    :param s_t: indicates time at which to begin plot
    :param e_t: indicates time at which to end plot
    :param s: indicates inclusive row index at which to begin plot. 
        defaults to 0 if not provided (and s_t not provided)
    :param e: indicates row index at which to end plot.
        defaults to row count if not provided (and e_t not provided)
    :param value_keys: if specified indicates the only columns to plot
    :param exclude_value_keys: specifies any columns to exclude from plotting
    :param show_dt: indicates whether to plot the time delta between 
        measurements against time
    """
    from matplotlib import pyplot as plt
    data = read_csv(fnom)
    assert s_t is None or s is None, "only one of s, s_t can be specified"
    assert e_t is None or e is None, "only one of e, e_t can be specified"
    assert value_keys is None or exclude_value_keys is None, (
        "only one of value_keys, exclude_value_keys can be specified"
    )

    if time_delta_key is not None:
        times = numpy.cumsum(data[time_delta_key])
        assert time_key not in data, (
            "when time_delta_key is specified, " + 
            "time_key must not refer to an existing column"
        )
        data[time_key] = times

    if s_t is not None:
        s = numpy.argmax(data[time_key] >= s_t)
        print ("s_t=%s -> s=%s" % (s_t, s))
    elif s is None:
        s = 0
        print("s=%s" % (s,))
    if e_t is not None:
        if len(data[time_key]) != 0 and e_t < data[time_key][-1]:
            e = numpy.argmin(data[time_key] <= e_t)
        else:
            e = len(data[time_key])
        print ("e_t=%s -> e=%s" % (e_t, e))
    elif e is None:
        e = len(data[time_key])
        print("e=%s" % (e,))

    if value_keys is None:
        exclude_value_keys = exclude_value_keys or []
        value_keys = [x 
                      for x in data.keys() 
                      if x != time_delta_key and x not in exclude_value_keys]
    ts = data[time_key][s:e]
    if show_dt:
        dts = ts[1:] - ts[:-1]
        plt.plot(ts[1:], dts)
        plt.ylabel("delta time")
        plt.xlabel("t")
        plt.show()
    for key in value_keys:
        if key == time_key: continue

        values = data[key][s:e]
        plt.plot(ts, values)
        plt.xlabel(time_key)
        plt.ylabel(key)
        plt.show()

def _sg_filter(x, m, k=0):
    """
    x = Vector of sample times
    m = Order of the smoothing polynomial
    k = Which derivative
    """
    mid = len(x) // 2        
    a = x - x[mid]
    expa = lambda x: list(map(lambda i: i**x, a)  )  
    A = numpy.r_[list(map(expa, range(0,m+1)))].transpose()
    Ai = numpy.linalg.pinv(A)

    return Ai[k]

def sg_smooth(x, y, size=5, order=2, deriv=0):
    """
    smooth data with a savitzky golay filter
    """

    if deriv > order:
        raise Exception( "deriv must be <= order")

    n = len(x)
    m = size

    result = numpy.zeros(n)

    for i in range(m, n-m):
        start, end = i - m, i + m + 1
        f = _sg_filter(x[start:end], order, deriv)
        result[i] = numpy.dot(f, y[start:end])

    if deriv > 1:
        result *= math.factorial(deriv)

    return result
