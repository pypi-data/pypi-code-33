#!/usr/bin/python3

import h5py

from anamnesis import obj_from_hdf5group, ClassRegister

# Register our class prefix so that we autoload our objects.  This
# allows loading all classes whose fully resolved name
# starts with test_classes1; e.g. test_classes1.SimplePerson
ClassRegister().add_permitted_prefix('test_classes1')

# Open our HDF5 file
f = h5py.File('test_script1.hdf5', 'r')

# Load the class from the HDF5 file using our
# obj_from_hdf5group method
s = obj_from_hdf5group(f['person'])

# Show that we have reconstructed the object
print(type(s))
print(s.name)
print(s.age)

# Close our HDF5 file
f.close()
