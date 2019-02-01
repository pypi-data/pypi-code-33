#!/usr/bin/python3

import h5py
from anamnesis import obj_from_hdf5file

from test_classes2 import ComplexPerson

# Create an example object
p = ComplexPerson('Bob', 75)
p.extra_data['hometown'] = 'Oxford'

print(p)
print(p.extra_data)

# Save the object out
f = h5py.File('test_script2_extradata.hdf5', 'w')
p.to_hdf5(f.create_group(p.hdf5_defaultgroup))
f.close()

# Delete our object
del p

# Re-load our object
p = obj_from_hdf5file('test_script2_extradata.hdf5')

# Show that we recovered the object and the extra data
print(p)
print(p.extra_data)
