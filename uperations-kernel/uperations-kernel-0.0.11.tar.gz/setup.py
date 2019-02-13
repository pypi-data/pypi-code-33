from distutils.core import setup
from setuptools import find_packages

setup(
    name='uperations-kernel',
    version='0.0.11',
    packages=find_packages(),
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open("README.rst").read(),
    author='Brice Aminou',
    author_email='brice.aminou@gmail.com',
    keywords='workflow tool',
    url='https://github.com/baminou/uperations-kernel'
)