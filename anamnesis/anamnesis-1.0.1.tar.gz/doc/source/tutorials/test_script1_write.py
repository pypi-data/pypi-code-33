#!/usr/bin/python3

import h5py

from test_classes1 import SimplePerson

# Create a person
s = SimplePerson('Fred', 42)

print(s.name)
print(s.age)

# Serialise the person to disk
f = h5py.File('test_script1.hdf5', 'w')
s.to_hdf5(f.create_group('person'))
f.close()
