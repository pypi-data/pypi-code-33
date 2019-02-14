#!/usr/bin/env python3

from setuptools import setup

setup(name='brom-spades',
      version='4.0',
      description='Scoring agent for Spades',
      author='Ralph Embree',
      author_email='ralph.embree@brominator.org',
      url='https://gitlab.com/ralphembree/brom-spades',
      scripts=['bin/brom-spades'],
      py_modules=["brom_spades"],
      keywords="brom-spades spades score scoring",
)
