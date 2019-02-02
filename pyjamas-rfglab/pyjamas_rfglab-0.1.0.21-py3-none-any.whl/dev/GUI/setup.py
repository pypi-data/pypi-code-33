from distutils.core import setup
from Cython.Build import cythonize
import numpy

setup(
    name="rimcore",
    ext_modules=cythonize("rimcore.pyx"),
    include_dirs=[numpy.get_include()]
)