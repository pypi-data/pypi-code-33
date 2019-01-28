
from setuptools import *
from setuptools.command.build_py import build_py

import shutil
import os
import sys

print(sys.argv) #debug

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="automaton_tools",
    version="0.1.8",
    author="oneengineer",
    author_email="oneengineer@gmail.com",
    description="some algorithm implementations for automaton and regular expressions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["antlr4-python3-runtime"],
    url="https://github.com/oneengineer/automaton_tools",
    packages=["automaton_tools","automaton_tools.regex_parser","automaton_tools.regex_parser.grammar"]
)
