#!/usr/bin/python3

from anamnesis import obj_from_hdf5file

# Read from our store
s = obj_from_hdf5file('test_script4.hdf5')

print(s.extra_data['airport_from'])
print(s.extra_data['airport_to'])
