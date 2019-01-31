import setuptools
from pathlib import Path

setuptools.setup(
    name="mapdf",
    version=1.0,
    long_description=Path("README.md").read_text(),
    pckage=setuptools.find_packages(exclude=["tests", "data"])

)
