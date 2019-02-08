from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='mad_import',
      version=version,
      description="For every module imported, mad_import adds all the recursive imports in a python file and imports that!!Hardcore",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='recursive import',
      author='kostas petsis',
      author_email='kostaspetsis@outlook.com',
      url='https://github.com/rivenblades/mad_import.git',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
