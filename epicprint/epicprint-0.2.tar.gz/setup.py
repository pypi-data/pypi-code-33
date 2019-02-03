import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='epicprint',  
     version='0.2',
     author="Anders Jürisoo",
     author_email="jurisoo@hotmail.com",
     description="Custom print with superpowers",
     url="https://github.com/ajthinking/epicprint",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )