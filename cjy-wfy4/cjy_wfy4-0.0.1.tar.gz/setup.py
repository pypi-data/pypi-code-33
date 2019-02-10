try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages
import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cjy_wfy4",
    version="0.0.1",
    packages=find_packages(),
    include_package_data=True,
    author="cjy",
    author_email="author@example.com",
    description="A small example package",
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
    'pygame==1.9.4'
    ]
)