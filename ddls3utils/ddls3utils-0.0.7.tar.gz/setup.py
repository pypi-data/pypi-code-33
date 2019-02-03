from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = 'ddls3utils',
    packages = ['ddls3utils'],
    version = '0.0.7',
    description = 'S3 utils',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author = 'Shen Wang',
    author_email = 'nedlitex0053@gmail.com',
    install_requires=['boto3'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)