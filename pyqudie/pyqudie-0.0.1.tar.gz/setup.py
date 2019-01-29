"""setup.py"""
from setuptools import setup, find_packages
from pyqudie import __version__, __author__, __name__, __doc__


setup(author=__author__,
      author_email='wc810267705@163.com',
      maintainer=__author__,
      name=__name__,
      packages=find_packages(exclude=('test', 'test.*')),
      package_dir = {'': '.'},
      long_description=open('README.md').read(),
      version=__version__,
      keywords='mongodb',
      description=__doc__,
      url="https://github.com/evi0s/pyqudie",
      install_requires=['pymongo>=3.7.2'],
      classifiers=[
          'Environment :: Console',
          'Programming Language :: Python :: 2.7',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ])