import os

from noaareport import NoaaReport

from datetime import datetime


def check_date(year, month, day):
    try:
        datetime(int(year), int(month), int(day))
        return True
    except Exception:
        return False

for year in range(2002, 2013):
    path = os.path.abspath("../..")
    path = os.path.join(path, "noaa-report\\reports\\" + str(year) + "_events\\")
    print(year, end="\n\n\n")
    for month in range(1, 13):
        for day in range(1, 32):
            if not check_date(year, month, day):
                continue
            report = NoaaReport(year, month, day, path)
            try:
                print(report.set_final_data())
            except:
                #print("Erro no dia {} {} {}".format(year, month, day))
                pass

