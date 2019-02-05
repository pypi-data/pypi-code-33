import setuptools

try:
    with open("README.md", "r") as fh:
        long_description = fh.read()
except:
    long_description = "Helper to automate Cloud AutoML (vision) operations"

setuptools.setup(
    name="automlhelper",
    version="0.0.1",
    author="Samuel Heinrichs",
    author_email="samuel@n2bbrasil.com",
    description="Helper to automate Cloud AutoML (vision) operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/N2BBrasil/automl-helper",
    install_requires=[r.split('==')[0] for r in open("requirements.txt").read().split("\n")],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)