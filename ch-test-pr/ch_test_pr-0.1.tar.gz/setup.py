import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='ch_test_pr',  
     version='0.1',
     author="Chris Hughes",
     author_email="christopher.hughes@bath.com",
     description="A test package",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/ch4413/Chpy",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
