import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pystack-sherryt400",
    version="0.0.1",
    author="Sheharyar Naseem",
    author_email="sherryfbi1994@gmal.com",
    description="A synchronized stack data structure for python 3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sherryt400/pystack",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)