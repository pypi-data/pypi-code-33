#!/usr/bin/env python3

import setuptools

with open("VERSION.txt", "r") as version_file:
    version = version_file.readline()
    print(version)

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

setuptools.setup(
    name="meylenplan",
    version=version,
    description="Fetches and displays the SchlemmerMeyle meal plan for today.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/ploth/meylenplan",
    author="Pascal Loth",
    author_email="pascal.loth@tuhh.de",
    license="GPLv3",
    packages=setuptools.find_packages(),
    scripts=['meylenPlan'],
    include_package_data=True,
    install_requires=[
        'beautifulsoup4>=4.5.1',
        'lxml>=4.2.5',
        'tabulate>=0.8.1',
        'urllib3>=1.22'
    ]
)
