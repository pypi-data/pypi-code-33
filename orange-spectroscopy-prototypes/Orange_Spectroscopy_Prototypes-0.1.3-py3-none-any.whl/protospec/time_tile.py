import time

import Orange
import orangecontrib.protospec

def test_time():
    t = time.time()
    data = Orange.data.Table("C:\\Users\\reads\\tmp\\aff-testdata\\2017-11-10 4X-25X\\2017-11-10 4X-25X.dmt")
    print(time.time() - t)

if __name__ == "__main__":
    test_time()