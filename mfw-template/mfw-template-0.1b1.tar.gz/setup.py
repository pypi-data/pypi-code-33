from setuptools import setup, find_packages
import sys, os

version = '0.1b1'

setup(name='mfw-template',
      version=version,
      description="Cookiecutter templates for Morp Framework",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Izhar Firdaus',
      author_email='kagesenshi.87@gmail.com',
      url='http://github.com/morpframework',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'cookiecutter',
          'click',
          'importscan',
          'pyyaml>=4.2b1',
          # -*- Extra requirements: -*-
      ],
      entry_points={
         'console_scripts': [
              'mfw-template=mfw_template.cli:cli',
          ]},
      )
