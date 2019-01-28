# To build the extension, run this setup script like so:
#
#    python setup.py build_ext --inplace
#
# or on Windows:
#
#    python setup.py build_ext --inplace --compiler=msvc
#
# To produce html annotation for a cython file, instead run:
#     cython -a myfile.pyx

from setuptools import setup
from setuptools.extension import Extension
from Cython.Distutils import build_ext

# Add autocython dir to the path if we're in the repo. This bit can be left out of
# your own setup.py file - it's just so that the example works without installing
# autocython:
import sys
import os
this_folder = os.path.dirname(os.path.abspath(__file__))
grandparent_folder = os.path.abspath(os.path.join(this_folder, '..', '..'))
if os.path.exists(os.path.join(grandparent_folder, 'autocython')):
    sys.path.insert(0, grandparent_folder)


from autocython import PLATFORM_SUFFIX

ext_modules = [Extension("hello_module" + PLATFORM_SUFFIX, ["hello_module.pyx"])]
setup(
    name = "hello_package",
    cmdclass = {"build_ext": build_ext},
    ext_modules = ext_modules,
)
