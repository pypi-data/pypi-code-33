#!/usr/bin/python3

import h5py
import numpy as np

from test_classes3 import CollectableSubjectStats, StatsCollection

# Create a collection to put our data into
collection = StatsCollection()

# Simulate 5 peoples worth of data
for person in range(5):
    # 10x10 zstats - low resolution image!
    zstats = np.random.randn(10, 10)
    # 100 trials - averaging 450ms
    rts = np.random.randn(100) * 450.0

    p = CollectableSubjectStats(zstats, rts)

    collection.append(p)

# Write the data to a file
f = h5py.File('test_script3.hdf5', 'w')
collection.to_hdf5(f.create_group('data'))
f.close()
