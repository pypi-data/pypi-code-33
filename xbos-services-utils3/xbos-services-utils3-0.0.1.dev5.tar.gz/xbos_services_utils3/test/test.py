from pathlib import Path
import sys
sys.path.append(Path.cwd().parent)
import utils3 as utils

import pandas as pd
import datetime
import pytz
import numpy as np


def test_resample():
    # Case 0. Pad. Align start/end with data start/end, interval is data interval, 1 column
    print("Case 0")
    start = datetime.datetime(year=2018, month=1, day=1, hour=0, minute=0, tzinfo=pytz.UTC)
    end = start + datetime.timedelta(hours=2)
    interval = 15

    date_range_1 = pd.date_range(start, end, freq=str(15) + "T")

    data = pd.Series(data=[1,2,3,4,5,6,7,8,9], index=date_range_1)

    print(utils.smart_resample(data, start, end, interval, method="interpolate"))
    print("")

    # Case 1. Pad. Align start/end with data start/end, interval is data interval, 1 column
    print("Case 1")
    start = datetime.datetime(year=2018, month=1, day=1, hour=0, minute=0, tzinfo=pytz.UTC)
    end = start + datetime.timedelta(hours=2)
    interval = 15

    date_range_1 = pd.date_range(start, end, freq=str(15) + "T")

    data = pd.DataFrame(data=[1,2,3,4,5,6,7,8,9], columns=["A"], index=date_range_1)

    print(utils.smart_resample(data, start, end, interval, method="pad"))
    print("")

    # Case 2. Pad. Align start/end with data start/end, interval is less than data interval, 1 column
    print("Case 2")
    start = datetime.datetime(year=2018, month=1, day=1, hour=0, minute=0, tzinfo=pytz.UTC)
    end = start + datetime.timedelta(hours=2)
    interval = 5

    date_range_2 = pd.date_range(start, end, freq=str(15) + "T")

    data = pd.DataFrame(data=[1,2,3,4,5,6,7,8,9], columns=["A"], index=date_range_2)

    print(utils.smart_resample(data, start, end, interval, method="pad"))
    print("")

    # Case 3. Pad. Align start/end with data start/end, interval is more than data interval, 1 column
    print("Case 3")
    start = datetime.datetime(year=2018, month=1, day=1, hour=0, minute=0, tzinfo=pytz.UTC)
    end = start + datetime.timedelta(hours=2)
    interval = 30

    date_range_3 = pd.date_range(start, end, freq=str(15) + "T")

    data = pd.DataFrame(data=[1, 2, 3, 4, 5, 6, 7, 8, 9], columns=["A"], index=date_range_3)

    print(utils.smart_resample(data, start, end, interval, method="pad"))
    print("")

    # Case 4. Pad. Align start/end with data start/end,
    # interval is more than data interval but not a multiple of end-start, 1 column
    print("Case 4")
    start = datetime.datetime(year=2018, month=1, day=1, hour=0, minute=0, tzinfo=pytz.UTC)
    end = start + datetime.timedelta(hours=2)
    interval = 21

    date_range_4 = pd.date_range(start, end, freq=str(15) + "T")

    data = pd.DataFrame(data=[1, 2, 3, 4, 5, 6, 7, 8, 9], columns=["A"], index=date_range_4)

    print(utils.smart_resample(data, start, end, interval, method="pad"))
    print("")

    # Case 5. Pad. Align start/end with data start/end,
    # interval is less than data interval but not a multiple of end-start, 1 column
    print("Case 5")
    start = datetime.datetime(year=2018, month=1, day=1, hour=0, minute=0, tzinfo=pytz.UTC)
    end = start + datetime.timedelta(hours=2)
    interval = 7

    date_range_5 = pd.date_range(start, end, freq=str(15) + "T")

    data = pd.DataFrame(data=[1, 2, 3, 4, 5, 6, 7, 8, 9], columns=["A"], index=date_range_5)

    print(utils.smart_resample(data, start, end, interval, method="pad"))
    print("")

    # Case 6. Pad. Don't align start/end with data start/end,
    # interval is not a multiple of end-start, 1 column
    print("Case 6")
    start = datetime.datetime(year=2018, month=1, day=1, hour=0, minute=0, tzinfo=pytz.UTC)
    end = start + datetime.timedelta(hours=2)
    interval = 15

    date_range_6 = pd.date_range(start, end , freq=str(15) + "T")

    data = pd.DataFrame(data=[1, 2, 3, np.nan, 5, 6, np.nan, 8, 9], columns=["A"], index=date_range_6)

    print(utils.smart_resample(data, start + datetime.timedelta(minutes=2), end + datetime.timedelta(minutes=3), interval, method="pad"))
    print("")

    # Case 7. Messed Pad. Don't align start/end with data start/end,
    # interval is not a multiple of end-start, 1 column, bad nan
    print("Case 7")
    start = datetime.datetime(year=2018, month=1, day=1, hour=0, minute=0, tzinfo=pytz.UTC)
    end = start + datetime.timedelta(hours=2)
    interval = 15

    date_range = pd.date_range(start, end , freq=str(15) + "T")

    data = pd.DataFrame(data=[np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan], columns=["A"], index=date_range)

    print(utils.smart_resample(data, start + datetime.timedelta(minutes=2), end + datetime.timedelta(minutes=12), interval, method="pad"))
    print("")

    # Case 8. Messed linear. Don't align start/end with data start/end,
    # interval is not a multiple of end-start, 1 column, bad nan
    print("Case 8")
    start = datetime.datetime(year=2018, month=1, day=1, hour=0, minute=0, tzinfo=pytz.UTC)
    end = start + datetime.timedelta(hours=2)
    interval = 15

    date_range = pd.date_range(start, end, freq=str(15) + "T")

    data = pd.DataFrame(data=[1, 2, 3, np.nan, 5, 6, np.nan, 8, 9], columns=["A"], index=date_range)

    print(utils.smart_resample(data, start + datetime.timedelta(minutes=2), end + datetime.timedelta(minutes=2), interval, method="interpolate"))
    print("")

    # Case 9. Messed linear. Don't align start/end with data start/end,
    # interval is not a multiple of end-start, 1 column, bad nan
    print("Case 9")
    start = datetime.datetime(year=2018, month=1, day=1, hour=0, minute=0, tzinfo=pytz.UTC)
    end = start + datetime.timedelta(hours=2)
    interval = 12

    date_range = pd.date_range(start, end, freq=str(15) + "T")

    data = pd.DataFrame(data=[1, 2, 3, np.nan, 5, 6, np.nan, 8, 9], columns=["A"], index=date_range)

    print(utils.smart_resample(data, start + datetime.timedelta(minutes=2), end + datetime.timedelta(minutes=2), interval, method="interpolate"))
    print("")

    # Case 9. Messed linear. Don't align start/end with data start/end,
    # interval is not a multiple of end-start, 2 column, bad nan
    print("Case 9")
    start = datetime.datetime(year=2018, month=1, day=1, hour=0, minute=0, tzinfo=pytz.UTC)
    end = start + datetime.timedelta(hours=2)
    interval = 12

    date_range = pd.date_range(start, end, freq=str(15) + "T")

    data = pd.DataFrame(data=np.array([[1, 2, 3, np.nan, 5, 6, np.nan, 8, 9], [-10,11,-12,13,14,15,16,-17, 18]]).T, columns=["A", "B"], index=date_range)
    print(utils.smart_resample(data, start + datetime.timedelta(minutes=2), end + datetime.timedelta(minutes=2), interval, method="interpolate"))
    print("")

    # Case 10. Messed pad. Don't align start/end with data start/end,
    # interval is not a multiple of end-start, 2 column, bad nan
    print("Case 9")
    start = datetime.datetime(year=2018, month=1, day=1, hour=0, minute=0, tzinfo=pytz.UTC)
    end = start + datetime.timedelta(hours=2)
    interval = 10

    date_range = pd.date_range(start, end, freq=str(15) + "T")

    data = pd.DataFrame(data=np.array([[1, 2, 3, np.nan, 5, 6, np.nan, 8, 9], [-10,11,-12,13,14,15,16,-17, 18]]).T, columns=["A", "B"], index=date_range)
    print(utils.smart_resample(data, start.astimezone(tz=pytz.timezone("America/Los_Angeles")) + datetime.timedelta(minutes=2), end + datetime.timedelta(minutes=2), interval, method="pad"))
    print("")

    date_range = pd.date_range(start, start, freq=str(15) + "T")

    data = pd.DataFrame(data=np.array([[1], [-10]]).T, columns=["A", "B"], index=date_range)
    print(utils.smart_resample(data, start.astimezone(tz=pytz.timezone("America/Los_Angeles")) + datetime.timedelta(minutes=2), end + datetime.timedelta(minutes=2), interval, method="pad"))
    print("")


def test_buildings():
    print(utils.get_buildings())


def test_all_zones():
    all_buildings = utils.get_buildings()
    for bldg in all_buildings:
        print("Building: %s" % bldg)
        print("Zones:")
        print(utils.get_zones(bldg))


if __name__ == "__main__":
    test_resample()
    test_buildings()
    test_all_zones()