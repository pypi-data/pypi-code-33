import setuptools
with open("README.rst", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='systemreports',  
     version='1.0.0',
     scripts=['systemreports'] ,
     author="Sriram Sreedhar",
     author_email="sriramsreedhar003@gmail.com",
     description="Generates System Report - Tested On Centos with Python 3.6",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/sriramsreedhar/systemreports.git",
     packages=setuptools.find_packages(),
     classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
     ],
 )
