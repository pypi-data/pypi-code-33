import setuptools
with open("README.rst", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='hellosriram',  
     version='1.0',
     scripts=['hellosriram'] ,
     author="Sriram Sreedhar",
     author_email="sriramsreedhar003@gmail.com",
     description="Hello Sriram",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/sriramsreedhar/hellosriram.git",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 2.7",
         "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
