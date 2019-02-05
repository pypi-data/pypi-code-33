from setuptools import setup, find_packages
from karvi import get_version

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="karvi",
    version=get_version(),
    author="Facundo Arano",
    author_email="aranofacundo@gmail.com",
    description="A small package with custom resources for Django projects.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/aranofacundo/karvi",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests", "log", "log.*", "*.log", "*.log.*"]),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Framework :: Django :: 2.0",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
