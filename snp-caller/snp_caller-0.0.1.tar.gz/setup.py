import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="snp_caller",
    version="0.0.1",
    author="Sergei Yakneen",
    author_email="llevar@gmail.com",
    description="Initial implementation of Rheos SNP caller",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/llevar/rheos",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)