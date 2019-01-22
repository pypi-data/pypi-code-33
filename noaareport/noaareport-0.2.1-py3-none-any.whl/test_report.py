import sys
import os

import pandas as pd

from noaareport import NoaaReport

def usage():
    print("Usage: report [YEAR] [MONTH] [DAY]")
    print("Optional: report [YEAR] [MONTH] [DAY] [EVENT_BEGIN] [EVENT_END]")
    print("\t-h\t this help message.")
    print("\nExample:")
    print("report 2002 4 9 12:40:00 13:00:00")
    print("\nWritten by Edison Neto (2018)")
    sys.exit()

if len(sys.argv) == 1:
    usage()

if sys.argv[1] == "--help" or sys.argv[1] == "-h":
    usage()

if len(sys.argv) < 4:
    print("You need more arguments.")
    sys.exit()

year = sys.argv[1]
month = sys.argv[2]
day = sys.argv[3]

path = os.path.abspath("../..")
path = os.path.join(path, "noaa-report\\reports\\" + year + "_events\\")

report = NoaaReport(year, month, day, path)
df = report.set_final_data()

print("index", end="\t")
for i in df.columns:
    print(i, end="\t")
print()

for i, row in df.iterrows():
    print(i, end="\t")
    for j in df.columns:
        print(row[j], end="\t")
    print()

if len(sys.argv) > 5:
    common_str = "0000-00-00 "
    begin = common_str + sys.argv[4]
    end = common_str + sys.argv[5]
    ars = report.get_active_region(begin, end)
    print(ars)
