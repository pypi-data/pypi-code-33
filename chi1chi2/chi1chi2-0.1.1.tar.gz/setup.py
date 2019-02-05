#!/usr/bin/env python

from setuptools import setup, find_packages

with open('requirements.txt') as fh:
    required = fh.readlines()

with open('README.rst') as f:
    readme = f.read()

setup(
    name='chi1chi2',
    version='0.1.1',
    author='Tomasz Seidler',
    url='https://bitbucket.org/tomeks86/chi1chi2',
    description='set of scripts for calculating linear and nonlinear optical properties of organic crystals',
    long_description=readme,
    license='MIT License',
    packages=find_packages(),
    install_requires=required,
    entry_points={
        'console_scripts': [
            'chi.from_fra = chi1chi2.from_fra:run',
            'chi.from_cif = chi1chi2.from_cif:run',
            'chi.from_crystal= chi1chi2.from_crystal:run',
            'chi.input_preparator = chi1chi2.input_preparator:run',
            'chi.main = chi1chi2.main:run',
        ],
    },
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Fortran',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Chemistry',
    ],
)
