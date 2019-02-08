"""
This script is used to install the package and all its dependencies. Run

    python setup.py install 
or
    python3 setup.py install

to install the package.
"""

# Copyright (C) 2018 Frank Sauerburger

from setuptools import setup

def load_long_description(*filenames):
    """
    Try to load all paragraph from any of the given file. If none of the
    files could be opened, return None.
    """
    for filename in filenames:
        try:
            with open(filename) as readme_file:
                content = readme_file.read()

            return content

        except FileNotFoundError as _:
            pass

    return None

setup(name='pyveu',
      version='0.1.0-alpha',
      packages=["pyveu", "pyveu.tests"],
      install_requires=['numpy', 'future', 'scipy', 'mock'],
      test_suite='pyveu.tests',
      description='Package to work with experimental data with'
                  ' uncertainties and units',
      long_description=load_long_description("README.rst"),
      url="https://gitlab.sauerburger.com/frank/pyveu",
      author="Frank Sauerburger",
      author_email="frank@sauerburger.com",
      keywords="physics value error uncertainty unit quantity",
      license="MIT",
      classifiers=["Intended Audience :: Developers",
                   "Intended Audience :: Education",
                   "Intended Audience :: Science/Research",
                   "License :: OSI Approved :: MIT License",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 2.7 ",
                   "Programming Language :: Python :: 3.4",
                   "Programming Language :: Python :: 3.5",
                   "Programming Language :: Python :: 3.6",
                   "Topic :: Scientific/Engineering :: Astronomy",
                   "Topic :: Scientific/Engineering :: Atmospheric Science",
                   "Topic :: Scientific/Engineering :: Bio-Informatics",
                   "Topic :: Scientific/Engineering :: Chemistry",
                   "Topic :: Scientific/Engineering :: Mathematics",
                   "Topic :: Scientific/Engineering :: Physics"])
