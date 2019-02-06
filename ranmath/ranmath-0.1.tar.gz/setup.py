import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='ranmath',  
    version='0.1',
    author="Pawel Talaga",
    author_email="talaga@protonmail.com",
    description="A Correlation Matrix Cleaning library based on Random Matrix Theory",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pawel-ta/ranmath",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
 )
