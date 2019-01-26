from explorepy import explore
from explorepy.tools import bin2csv
explore = explore.Explore()
explore.connect()
# explore.acquire()
explore.record_data("test1")


## bin2csv test:
filename = "DATA054.BIN"
bin2csv(filename)
