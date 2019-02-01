#!/usr/bin/python3

from anamnesis import obj_from_hdf5file

import test_classes1  # noqa: F401

# Load the class from the HDF5 file
s = obj_from_hdf5file('test_script1.hdf5')

# Show that we have reconstructed the object
print(type(s))
print(s.name)
print(s.age)


# Demonstrate how to specifically choose which group to load
s2 = obj_from_hdf5file('test_script1.hdf5', 'person')

# Show that we have reconstructed the object
print(type(s))
print(s.name)
print(s.age)
