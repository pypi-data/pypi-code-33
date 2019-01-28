
# import pytest

import pandas as pd
# import numpy as np


from pyrle import Rle
r = Rle([1, 2, 3], [4, 5, 6])

print(r[1:2])
df = pd.DataFrame({"Start": [1, 1, 5], "End": [2, 4, 100]})
print(r[df])

import pyranges as pr

gr = pr.data.chipseq()
c = gr.coverage()

r_ = c[gr.sort()]

for k, v in r_.items():

    print(k)
    for a, b in v:
        if a[0] != 25:
            print(a, b)
