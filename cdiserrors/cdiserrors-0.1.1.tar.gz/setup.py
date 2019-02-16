
from setuptools import setup, find_packages

setup(
    name="cdiserrors",
    version='0.1.1',
    description="The auth system for the gdcapi.",
    license="Apache",
    packages=find_packages(),
    install_requires=[
        'cdislogging>=0.0.2',
        'Flask',
        'Werkzeug',
    ],
)
