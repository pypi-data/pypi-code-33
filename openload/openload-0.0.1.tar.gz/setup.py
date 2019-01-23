#!/usr/bin/env python

from distutils.core import setup

setup(
    name='openload',
    version='0.0.1',
    description='Third-party library for Openload API',
    author='Dong Guo',
    author_email='guodong000@gmail.com',
    license='WTFPL',
    url='https://github.com/guodong000/openload-python-sdk',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=['openload'],
    install_requires=['requests'],
    python_requires='>=3',
)