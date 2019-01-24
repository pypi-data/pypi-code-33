import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='wangle',  
    version='0.1.3',
    author="Ben Harpin",
    author_email="benjaminharpin@gmail.com",
    description="A python library for natural language manipulation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/benjaminharpin/wangle",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
