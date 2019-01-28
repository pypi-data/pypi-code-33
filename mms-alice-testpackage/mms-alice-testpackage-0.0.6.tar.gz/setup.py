import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mms-alice-testpackage",
    version="0.0.6",
    author="Josef Goppold",
    author_email="goppold@mediamarktsaturn.com",
    description="This is a test",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EastOfGondor/mms-alice-python-packages",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",   
    ],
)