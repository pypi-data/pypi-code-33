import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lambdev",
    version="0.1.0",
    author="Justin Santoro",
    author_email="jzsantoro14@gmail.com",
    description="A small package that simplifies developing AWS Lambda functions locally",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/justinsantoro/lambdev",
    packages=setuptools.find_packages(),
    install_requires=['boto3'],
    classifiers=[
        "Programming Language :: Python",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
