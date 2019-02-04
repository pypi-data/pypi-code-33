import sys
sys.path.insert(0,"./src")
from python_openapi3 import VERSION

from setuptools import setup

setup(
    name='python_openapi3',
    version=VERSION,
    packages=['python_openapi3', 'python_openapi3.openapi_specification'],
    package_dir={'': 'src'},
    install_requires=["future"],
    url='https://github.com/joranbeasley/python_openapi3',
    license='GPL',
    author='Joran Beasley',
    author_email='joranbeasley@gmail.com',
    description='attempts to provide python binding and validation to all of OAS3.0 spec'
)
