

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='PyNFVSDK',


    version='0.1dev3',

    description='an SDK to faciliate REST calls for various Cisco NFV management platforms',
    long_description='an SDK to faciliate REST calls for various Cisco NFV management platforms, such as NFVIS and DNA-Center'
,

    url='https://github.com/kriswans/',


    author='Kris Swanson, Wade Lehrschall, Aaron Warner ',
    author_email='kriswans@cisco.com, wlehrsch@cisco.com, aawarner@cisco.com',


    license='MIT',

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',


        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',


        'License :: OSI Approved :: MIT License',



        'Programming Language :: Python :: 3.7',
    ],


    keywords=['NFV','REST','Cisco NFV'],

	packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    python_requires='>=3.5',

    install_requires=['requests'],

	package_data={
        'PyNFVSDK': [],
    },


    data_files=[],



)
