import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mms_python_logger",
    version="0.0.1",
    author="Tobias hoke",
    author_email="hoke@mediamarktsaturn.com",
    description="A custom MMS/Alice log module for python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EastOfGondor/mms-alice-python-logger",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)