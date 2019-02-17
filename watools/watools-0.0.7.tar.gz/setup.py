# -*- coding: utf-8 -*-
"""
Created on Tue Aug 07 14:43:01 2018

@author: tih
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="watools",
    version="0.0.7",
    author="Tim Hessels",
    author_email="t.hessels@un-ihe.org",
    description="Python module for retrieval of hydrologic, atmospheric, and remote sensing data used for Water Accounting.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wateraccounting/watools",
    packages=setuptools.find_packages(),
	install_requires=[
        'Pillow>=5.2.0',
		'beautifulsoup4>=4.6.0',
		'earthengine-api>=0.1.143',
		'h5py>=2.8.0',
		'httplib2>=0.11.3',
		'joblib>=0.12.0',
		'lxml>=4.2.4',
		'netCDF4>=1.4.0',
		'numpy>=1.14.5',
		'pandas>=0.23.3',
		'paramiko>=2.4.1',
		'pyshp>=1.2.12',
		'request',
		'scipy>=1.1.0',
		'urllib3>=1.23',
        'oauth2client>=4.1.2'		
    ],
	extras_require={
        ':python_version <= "2.7"': [
        'pyproj'	
        ]},
    classifiers=(
	    "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ),
)