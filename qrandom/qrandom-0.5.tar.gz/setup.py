import setuptools

with open("README.md", "r") as fh:

    long_description = fh.read()

setuptools.setup(

     name='qrandom',  

     version='0.5',

     author="Ravin Kumar",

     author_email="mr.ravin_kumar@hotmail.com",

     description="A Docker This repository contains the source code of research paper titled: \" A generalized quantum algorithm for assuring fairness in random selection among 2^n participants\"",

     long_description=long_description,

   long_description_content_type="text/markdown",

     url="https://github.com/mr-ravin/QrandomSelection",

     packages=setuptools.find_packages(),

     classifiers=[

         "Programming Language :: Python :: 3",

         "License :: OSI Approved :: GNU General Public License (GPL)",

         "Operating System :: OS Independent",

     ],

 )
