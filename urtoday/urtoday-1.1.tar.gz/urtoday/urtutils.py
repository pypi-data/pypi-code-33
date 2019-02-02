# URTutils
import os
_homedir = os.environ["HOME"]
def pad_date(l):
    y = l[0]
    m = l[1]
    d = l[2]
    while len(y)<4:
        y = "0" + y
    while len(m)<2:
        m = "0" + m
    while len(d)<2:
        d = "0" + d
    return [y, m, d]
def submit_to_user_file(day, rating):
    cur = get_user_file()
    if type(day)==type([]):
        day = list(map(str, day))
        day = pad_date(day)
        day = "".join(day)
    if not cur:
        create_user_file()
        cur = get_user_file()
    cur[day] = rating
    update_user_file(cur)

def get_user_file():
    try:
        f = open("{}/.urtoday".format(_homedir), "r")
    except FileNotFoundError:
        return False
    lines = f.readlines()
    cur = {}
    for line in lines:
        l2 = line.split()
        date = l2[0]
        rate = l2[1]
        cur[date] = int(rate)
    return cur

def create_user_file():
    f = open("{}/.urtoday".format(_homedir), "x")
    f.close()
    return True

def update_user_file(cur):
    f = open("{}/.urtoday".format(_homedir), "w")
    lines = []
    for ind in cur:
        date = ind
        rate = cur[ind]
        line = "{} {}\n".format(date, rate)
        lines += [line]
    f.writelines(lines)
    f.close()


def get_day_range_values(days):
    import time as _time
    import datetime as _datetime
    today = list(_time.localtime())[0:3]
    stoday = list(map(str, today))
    stoday = pad_date(stoday)
    dttoday = _datetime.date(*today)
    dtdelta = _datetime.timedelta(days=days)
    dtfirstday = dttoday - dtdelta
    firstdaystr = [str(dtfirstday.year), str(dtfirstday.month), str(dtfirstday.day)]
    firstdaystr = pad_date(firstdaystr)
    firstdaystr = "".join(firstdaystr)
    f = get_user_file()
    lk = list(f.keys())
    firstdayindex = lk.index(firstdaystr)
    newkeys = lk[firstdayindex:]
    retlist = []
    for key in newkeys:
        try:
            retlist += [f[key]]
        except:
            pass
    return retlist

def get_average(days):
    vals = get_day_range_values(days)
    s = sum(vals)
    count = len(vals)
    avg = s / count
    return avg

def get_min(days):
    vals = get_day_range_values(days)
    return min(vals)

def get_max(days):
    vals = get_day_range_values(days)
    return max(vals)

def get_median(days):
    vals = get_day_range_values(days)
    median = vals[int(len(vals)/2)] if len(vals)%2==1 else (vals[int(len(vals)/2)-1]+vals[int(len(vals)/2)])/2
    return median

