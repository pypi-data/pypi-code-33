import os.path

#from distutils.core import setup
from setuptools import setup

version = '0.0.2'
packages = ['extranormal3']

#package_data = {'extranormal.addons': ['imgs/*']}
#scripts = [os.path.join('scripts', f) for f in ['ab_test.py']]

'''
if os.name != 'posix':  # windows
    scripts = [os.path.join('scripts', f) for f in ['test.py']]
'''

setup(name='extranormal3',
      version=version,
      description='Quick normalization of a bunch of Quick-EXAFS spectra',
      author='Olga Roudenko',
      author_email='olga.roudenko@synchrotron-soleil.fr',
      license='GPL >= v.3',
      platforms=['Linux', 'Windows'],
      packages=packages,
      #package_data=package_data,
      #scripts=scripts
      )
