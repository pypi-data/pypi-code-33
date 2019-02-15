""" setuptools based setup module for scotty.py
continuous experimentation framework
"""
from setuptools import setup

setup(
    setup_requires=['pytest-runner', 'pbr>=2.0.0'],
    tests_require=['pytest'],
    pbr=True
)
