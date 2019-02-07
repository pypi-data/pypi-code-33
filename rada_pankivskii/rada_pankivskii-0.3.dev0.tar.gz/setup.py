from setuptools import setup, find_packages
import sys, os

version = '0.3'

requirements = [
               'iso8601'
]

setup(name='rada_pankivskii',
      version=version,
      description="",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Vitalii Pankivskii',
      author_email='mr.pankivskii@gmail.com',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=requirements,
      entry_points={
            'console_scripts':[
                  'rada = rada_pankivskii.app:main'
            ]
      },
      )
