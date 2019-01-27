# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='daynextprev',
    version='0.0.6',
    description='calculate next/prev day from y/m/d input',
    author='Tomotaka Ito',
    author_email='tomotaka.ito@gmail.com',
    url='https://github.com/tomotaka/day-nextprev',
    packages=find_packages(),
    license=open('LICENSE').read(),
    include_package_data=True,
    install_requires=[
    ],
    tests_require=['nose'],
    test_suite='nose.collector'
)
