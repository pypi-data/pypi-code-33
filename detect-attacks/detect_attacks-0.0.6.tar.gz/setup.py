import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="detect_attacks",
    version="0.0.6",
    author="Van-Kha Nguyen",
    author_email="hainguyen579@gmail.com",
    description="A python package to detect attacks via networks",
    long_description=long_description,
    long_description_content_type="text/markdown",
   # url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

### 0.0.1
# initial project

### 0.0.2
# declare and import deepmg

### 0.0.3,4,5
# readme