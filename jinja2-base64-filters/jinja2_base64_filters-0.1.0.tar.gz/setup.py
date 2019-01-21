# coding: utf-8
import io
import os
import re

from setuptools import find_packages, setup


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type(u"")
    with io.open(filename, mode="r", encoding="utf-8") as fd:
        return re.sub(text_type(r":[a-z]+:`~?(.*?)`"), text_type(r"``\1``"), fd.read())


setup(
    keywords="jinja2_base64_filters",
    name="jinja2_base64_filters",
    version="0.1.0",
    url="https://github.com/lumapps/jinja2_base64_filters",
    license="MIT",
    author="Timothée GERMAIN",
    author_email="timothee@lumapps.com",
    description="Tiny jinja2 extension to add b64encode and b64decode filters.",
    long_description=read("README.rst"),
    packages=find_packages(exclude=("tests",)),
    install_requires=["jinja2"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
)
