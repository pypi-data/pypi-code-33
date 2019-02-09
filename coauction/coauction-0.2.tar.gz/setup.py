import setuptools

with open("README.md", "r") as fh:

    long_description = fh.read()

setuptools.setup(

     name='coauction',  

     version='0.2',

     author="Ravin Kumar",

     author_email="mr.ravin_kumar@hotmail.com",

     description="This repository will contain the source codes for newly proposed auction systems in our proposed economics research paper. Targeted to update the repository before : 15th March 2019",

     long_description=long_description,

   long_description_content_type="text/markdown",

     url="https://github.com/mr-ravin/collaborative-auction",

     packages=setuptools.find_packages(),

     classifiers=[

         "Programming Language :: Python :: 3",

         "License :: OSI Approved :: GNU General Public License (GPL)",

         "Operating System :: OS Independent",

     ],

 )
