import codecs
import os
import sys

try:
	from setuptools import setup, find_packages
except:
	from distutils.core import setup

def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "luo",
    version = "0.0.3",
    description = "tools for luo",
    long_description = read("README.txt"),
    classifiers =
	[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
		'Topic :: Scientific/Engineering :: Astronomy',
		'Topic :: Scientific/Engineering :: GIS',
		'Topic :: Scientific/Engineering :: Mathematics',
		'Intended Audience :: Science/Research',
		'Intended Audience :: Developers',
		'Intended Audience :: Information Technology',
    ],
    install_requires=
	[

    ],
    keywords = "tools",
    author = "yucheng",
    author_email = "yuchengluo@outlook.com",
    url ="https://github.com/guruL/luo",
    license = "MIT",
    packages = find_packages(),
    include_package_data= True,
    zip_safe= True,
)