#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('README_pypi.md') as f:
    long_description = f.read()

setup(name='graphannis',
      version='0.17.0',
      description='graphANNIS Python API',
      author='Thomas Krause',
      author_email='thomaskrause@posteo.de',
      url='https://github.com/korpling/graphANNIS-python/',
      long_description=long_description,
      long_description_content_type='text/markdown',
      packages=['graphannis'],
      include_package_data=True,
      setup_requires=["cffi>=1.0.0"],
      cffi_modules=["package/graphannis_build.py:ffibuilder"],
      install_requires=["cffi>=1.0.0","networkx"],
      classifiers=(
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows"
      ),
     )
