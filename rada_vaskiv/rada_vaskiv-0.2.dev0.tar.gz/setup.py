from setuptools import setup, find_packages
import sys, os

version = '0.2'

requires = [
      'iso8601',
]

setup(name='rada_vaskiv',
      version=version,
      description="",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Taras Vaskiv',
      author_email='',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      entry_points={
            'console_scripts':[
                  'rada = rada_vaskiv.app:main'
            ]
      },
      )
