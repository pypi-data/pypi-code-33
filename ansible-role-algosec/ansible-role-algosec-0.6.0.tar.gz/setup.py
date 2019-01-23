from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="ansible-role-algosec",
    version="0.6.0",
    packages=["library"],
    url="https://github.com/AlmogCohen/ansible-role-algosec",
    license="MIT",
    author="Almog Cohen",
    description="Set of Ansible modules for AlgoSec services management",
    long_description=long_description,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
    ],
    install_requires=[
        "algosec>=1.3.1",
        "ansible",
        "marshmallow",
        "urllib3",
    ],
)
