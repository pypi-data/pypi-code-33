#!/usr/bin/env python

from distutils.core import setup

setup(
    # Application name:
    name="aws-sh",


    # Version number (initial):
    version=open("VERSION.txt").readline().rstrip(),

    # Application author details:
    author="Steven hk Wong",
    author_email="steven@wongsrus.net",

    # Packages
    packages=["aws-sh", "aws-sh/classes"],

    # Include additional files into the package
    include_package_data=True,

    package_data={'aws-sh': [ 'LICENSE.txt', 'README.txt', 'CHANGES.txt' ]},

	  scripts=[ 'scripts/aws-sh' ],

    # Details
    url="http://pypi.python.org/pypi/aws-sh/",

    #
    license="LICENSE.txt",
    description="A shell for AWS commands.",

    long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
        "boto3","aws-cmd",
    ],
)
