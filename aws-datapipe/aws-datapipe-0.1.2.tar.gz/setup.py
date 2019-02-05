from setuptools import setup
import sys
import re
import codecs
import os.path

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

requires = ['pyfiglet',
            'awscli']

setup(
    name='aws-datapipe',
    version=find_version("awsdatapipe", "__init__.py"),
    description='Tool for creating AWS data pipeline to export data from any DynamoDB table to an S3 bucket',
    long_description=open('README.rst').read(),
    url='https://github.com/tmxak/aws-datapipe',
    author='Maxim Tacu',
    author_email='maxtacu95@gmail.com',
    license='MIT',
    packages=['awsdatapipe'],
    install_requires=requires,
    package_data={
        'awsdatapipe': ['data/*.json']
    },
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        'Topic :: System :: Systems Administration',
        'Intended Audience :: System Administrators',
    ],
    scripts=['awsdatapipe/aws-datapipe'],
    include_package_data=True,
    zip_safe=False)