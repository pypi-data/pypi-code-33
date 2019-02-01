#!/usr/bin/python3

from test_classes2 import ComplexPerson, ComplexPlace  # noqa: F401

# Load the classes from the HDF5 file using
# the default hdf5group names
s = ComplexPerson.from_hdf5file('test_script2.hdf5')
l = ComplexPlace.from_hdf5file('test_script2.hdf5')

# Show that we have reconstructed the object
print("Person")
print(type(s))
print(s.name)
print(s.age)


print("Place")
print(type(l))
print(l.location)
