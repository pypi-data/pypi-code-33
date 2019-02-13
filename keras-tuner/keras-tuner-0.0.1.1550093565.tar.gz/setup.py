"""Setup script."""
from __future__ import absolute_import

from setuptools import find_packages
from setuptools import setup
import time

version = "0.0.1"
stub = str(int(time.time()))  # Used to increase version automagically.
version = version + '.' + stub

setup(
    name="keras-tuner",
    version=version,
    description="Hypertuner for Keras",
    author='Luca Invernizzi',
    author_email='invernizzi.l@gmail.com',
    url='https://fixme',
    license='MIT',
    install_requires=[
    ],
    packages=find_packages()
)
