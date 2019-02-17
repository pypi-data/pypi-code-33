from setuptools import find_packages, setup


# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(
    name='xbos-services-utils2',
    version='0.0.6dev1',
    packages=find_packages(),
    # license='Creative Commons Attribution-Noncommercial-Share Alike license',
    author='Daniel Lengyel',
	author_email='daniel.lengyel@berkeley.edu',
    description="Utility functions for xbos services using Python 2.7.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
    	"pandas == 0.22.0",
    	"numpy == 1.14.0",
    	"pytz == 2018.3",
        "PyYAML==3.12",
    ],
)
