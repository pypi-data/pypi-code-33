#!/usr/bin/env python
import sys
from setuptools import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='integer-gantt',
    version='0.0.1.2',
    description='integer-gantt: quick and dirty gantt chart generator.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Kevin Glasson',
    author_email='kevinglasson+integer-gantt@gmail.com',
    url='https://github.com/kevinglasson/integer-gantt.git',
    packages=['integer_gantt'],
    install_requires=['plotly', 'psutil', 'numpy'],
    python_requires='>=3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3'
    ]
)