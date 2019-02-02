from distutils.core import setup
from Cython.Build import cythonize
import numpy

setup(
    ext_modules=cythonize("rimcore.pyx"),
    include_dirs=['/Users/rodrigo/src/pyjamas_package/rimage_c/', numpy.get_include()]
)