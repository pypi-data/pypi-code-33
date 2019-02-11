# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('../README.md') as f:
    readme = f.read()

with open('../LICENSE') as f:
    license = f.read()

setup(
    name='pieqt',
    version='0.0.2',
    description='simple description',
    long_description=readme,
    author='kostas_petsis',
    author_email='kostaspetsis@outlook.com',
    url='https://github.com/rivenblades/pieqt',
    license=license,
    py_modules={'App','pieqt'}
)
