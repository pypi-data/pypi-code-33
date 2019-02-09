from __future__ import print_function, division
import numpy as np


# float16:  At i=0/2147483647 (0.00%)...
#           Found inaccuracy at 2049. Got unexpected 2048. Float value is 2048.000000000000
# float32:  At i=16000000/2147483647 (0.75%)...
#           Found inaccuracy at 16777217. Got unexpected 16777216. Float value is 16777216.000000000000
# float64:  At i=2147000000/2147483647 (99.98%)...
#           No inaccuracies found.
# float128: At i=2147000000/2147483647 (99.98%)...
#           No inaccuracies found.
def main():
    min_value = np.iinfo(np.int32).min
    max_value = np.iinfo(np.int32).max

    for dtype in [np.float16, np.float32, np.float64, np.float128]:
        dtype = np.dtype(dtype)
        print("")
        print("===================")
        print("dtype=%s" % (dtype.name,))
        print("===================")

        i = 0
        arr = np.full((1,), i, dtype=dtype)
        while True:
            if i % (1000*1000) == 0:
                print("At i=%d/%d (%.2f%%)..." % (i, max_value, 100*(i/max_value)))

            arr_int = arr.astype(np.int64)
            if arr_int[0] != i:
                print("Found inaccuracy at %d. Got unexpected %d. Float value is %.12f" % (i, int(arr_int[0]), arr[0]))
                break

            i += 1
            arr = arr + 1
            if i > max_value:
                print("No inaccuracies found.")
                break


if __name__ == "__main__":
    main()
