#!/usr/bin/env python

from setuptools import setup, find_packages

with open('requirements.txt') as fh:
    required = fh.readlines()

setup(
    name='chi1chi2',
    version='0.1.0',
    author='Tomasz Seidler',
    url='https://bitbucket.org/tomeks86/chi1chi2',
    description='set of scripts for calculating linear and nonlinear optical properties of organic crystals',
    license='MIT',
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
    }
)
