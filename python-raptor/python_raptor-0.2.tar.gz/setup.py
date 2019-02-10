"""Setup For PIP"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="python_raptor",
    version="0.2",
    author="Roshan Jignesh Mehta",
    author_email="sonicroshan122@gmail.com",
    scripts=['script/raptor.py'],
    description="An Easy Way To Benchmark Your Python Code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SonicRoshan/Raptor",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
