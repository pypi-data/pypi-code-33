#!/usr/bin/env python
from setuptools import setup, find_packages

with open("./requirements.txt", "r") as f:
  dep_packages = f.readlines()
  # remove local install.
  dep_packages = [x.strip() for x in dep_packages if not x.startswith("-e")]
  # remove unnecessary packages.
  dep_packages = [x for x in dep_packages if not x.startswith("certifi")]

setup(
    name="tmw",
    version="0.0.0",
    description="",
    keywords="",
    url="",
    author="",
    author_email="",
    packages=find_packages(where="src"),
    package_data={
        '': ['LICENSE', 'NOTICE'],
        'requests': ['*.pem']
    },
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "foo = my_package.some_module:main_func",
            "bar = other_module:some_func",
        ],
    },
    install_requires=dep_packages,
    extras_require={
        "tf": ["tensorflow>=1.0.0"],
    },
    include_package_data=True,
    zip_safe=False)
