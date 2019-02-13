import setuptools
from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='Boomstick',
    author='The Fuel Rats Mischief',
    url='https://github.com/FuelRats/boomstick',
    version='1.0',
    packages=['boomstick', ],
    license='BSD-3-Clause',
    long_description=long_description,
    install_requires=['coloredlogs'],
    classifiers=["Programming Language :: Python :: 3",
                 "License :: OSI Approved :: BSD License",
                 "Operating System :: OS Independent",
                 "Development Status :: 2 - Pre-Alpha",
                 "Intended Audience :: Developers"],
)