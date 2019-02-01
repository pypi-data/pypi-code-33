#!/usr/bin/python3

from anamnesis import obj_from_hdf5file

import test_classes2  # noqa: F401

# Demonstrate reading a file which has the old class name
# in the HDF5 file
s = obj_from_hdf5file('test_script2_aliases.hdf5', 'person')

# Show that we have reconstructed the object
print("Person")
print(type(s))
print(s.name)
print(s.age)
