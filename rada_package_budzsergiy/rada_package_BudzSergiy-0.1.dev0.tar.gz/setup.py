from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='rada_package_BudzSergiy',
      version=version,
      description="Rada with abstract factory",
      long_description="""Ukraine and Poland radas""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='abstract factory python',
      author='Budz Sergiy',
      author_email='',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'iso8601'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
