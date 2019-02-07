from setuptools import setup

version = "1.0.0"

with open("./README.md") as fd:
    long_description = fd.read()

setup(
    name="shelllnk",
    version=version,
    description="Package for parsing Microsoft Shell Link (.lnk) files",
    long_description = long_description,
    long_description_content_type="text/markdown",
    author="Lee Kamentsky",
    packages=["shelllnk"],
    entry_points = dict(
        console_scripts=[
            "shelllnk-info=shelllnk.main:main"
        ]),
    url="https://github.com/leekamentsky/shelllnk",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3"
    ]
    )