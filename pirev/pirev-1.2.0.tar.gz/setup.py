import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pirev",
    version="1.2.0",
    author="Sam Jordan",
    author_email="sam@jrdn.ca",
    description="Raspberry Pi revision utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/samjrdn/pirev-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
