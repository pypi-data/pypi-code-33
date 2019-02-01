#-----------------------------------------------------------------------------
# Name:        setup
# Purpose:    
# Author:      Aric Sanders
# Created:     12/30/2017
# License:     MIT License
#-----------------------------------------------------------------------------
""" Module for distribution, this module contains the setup for pip. After updating the version and information, a command line message
python setup.py sdist, and then python setup.py sdist upload. Make sure the password is up to date in the .pypirc file and it is located in 
a folder that setup can find. I had to define the %HOME% environmental variable on 10/02/2018 to make it work.  """
#-----------------------------------------------------------------------------
# Standard Imports
from setuptools import setup, find_packages

#-----------------------------------------------------------------------------
# Third Party Imports

#-----------------------------------------------------------------------------
# Module Constants

#-----------------------------------------------------------------------------
# Module Functions

#-----------------------------------------------------------------------------
# Module Classes

#-----------------------------------------------------------------------------
# Module Scripts

#-----------------------------------------------------------------------------
# Module Runner
if __name__ == '__main__':


    setup(
        name='pyMez',
		
		package_dir={'':'src'} ,
        packages=find_packages('src'),  # this must be the same as the name above
		#include_package_data=True,
		package_data = {'': ['*.txt', '*.xml', '*.html', '*.ipynb','*.xsl','*.s*p'],},
        version='1.3.20',
        description='Measurement, Analysis and Data Management Software. To load the API interface use from pyMez import *.',
		long_description="""pyMez is a python package born out of the daily needs of a laboratory scientist. In particular, there is a constant need to use external equipment to acquire data, store that data in a sensible way, analyze the stored data, and generate collections and reports after analyzing the data. In the world of scientific computation there is an endless universe of solutions to do this, however none of the solutions met my personal daily needs and philosophy simultaneously. This package tries to stitch together many tools to meet those needs, while serving as a backend library to a webserver. It thus has many dependencies. Some of the dependencies are os specific, however the lack of them should not prevent operation. Although it currently has a single primary developer, it is my hope that it will be adopted by at least 10's of people and help them accomplish their daily scientific goals.""",
        author='Aric Sanders',
        author_email='aric.sanders@gmail.com',
        url='https://github.com/aricsanders/pyMez',  # use the URL to the github repo
        download_url='https://github.com/aricsanders/pyMez.git',  # I'll explain this in a second
        keywords=['measurement', 'data handling', 'example'],  # arbitrary keywords
        classifiers=['Programming Language :: Python'],
		license="MIT",
		install_requires=['markdown','numpy','pandas',"Pillow","pdfkit",
		"pdoc","networkx","pyvisa","scipy","matplotlib",'pywin32;platform_system=="Windows"','pythonnet;platform_system=="Windows" and python_version<"3.4"',"lxml"], 
    )
    