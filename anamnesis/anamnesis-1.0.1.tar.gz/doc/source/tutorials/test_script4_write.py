#!/usr/bin/python3

import h5py

from anamnesis import Store

# Create a Store
s = Store()

s.extra_data['airport_from'] = 'Manchester'
s.extra_data['airport_to'] = 'Schipol'

# Write the store into a file
f = h5py.File('test_script4.hdf5', 'w')
s.to_hdf5(f.create_group('data'))
f.close()
