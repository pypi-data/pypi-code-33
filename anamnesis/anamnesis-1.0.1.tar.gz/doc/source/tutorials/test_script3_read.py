#!/usr/bin/python3

from anamnesis import obj_from_hdf5file

import test_classes3  # noqa: F401

# Load our collection of data
c = obj_from_hdf5file('test_script3.hdf5')

# Demonstrate how we have access to each individual object
for p in c.members:
    print(p.zstats.shape, p.zstats.min(), p.zstats.max())

# Make sure that our cache is up-to-date before we demonstrate
# the stacked data methods
c.update_cache()

# Demonstrate that we have access to stacked versions of the data
print(c.zstats.shape)
print(c.rts.shape)
