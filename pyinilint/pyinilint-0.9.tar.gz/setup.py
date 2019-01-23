"""setuptools configuration for the pyinilint package.

See: https://packaging.python.org/tutorials/packaging-projects
"""

import setuptools

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name="pyinilint",
    version="0.9",
    author="Daniel J. R. May",
    author_email="daniel.may@danieljrmay.com",
    description="A linter and inspector for INI format files",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/danieljrmay/pyinilint",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
    ],
    entry_points={
        "console_scripts": ["pyinilint=pyinilint.pyinilint:main"],
    },
    test_suite="pyinilint.tests",
    include_package_data=False,
)
