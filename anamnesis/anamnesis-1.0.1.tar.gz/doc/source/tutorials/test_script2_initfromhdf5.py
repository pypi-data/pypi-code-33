#!/usr/bin/python3

from anamnesis import obj_from_hdf5file

from test_classes2 import ComplexPerson  # noqa: F401

# Load the train object and watch for the printed output from the
# init_from_hdf5 function
p = obj_from_hdf5file('test_script2.hdf5', 'train')
