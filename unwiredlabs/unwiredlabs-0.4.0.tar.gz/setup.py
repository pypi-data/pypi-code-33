# -*- coding: utf-8 -*-

import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

exec(open('unwiredlabs/version.py').read())

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='unwiredlabs',
    version=__version__,
    packages=['unwiredlabs'],
    include_package_data=True,
    license='BSD License',  # example license
    description='Unwiredlabs Location API client.',
    long_description=README,
    url='https://github.com/anfema/python-unwired',
    author='Johannes Schriewer',
    author_email='j.schriewer@anfe.ma',
    install_requires=[
        "requests >= 2.10.0",
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
    ],
)
