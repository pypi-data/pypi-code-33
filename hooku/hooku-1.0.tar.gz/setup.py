
from setuptools import setup 
  
#Long description
long_description = '''The package contains a simple function that fetches the note that has been pasted into a website called primapad.com.

Step 1: Create a new note at http://primapad.com/<some_unique_file_name>
Step 2:	To fetch the note whenever you want using python, follow the code,

import hooku
x = hooku.get('<your_unique_file_name>') //Fetches the note pasted in the url in text format
print(x) //Prints the note pasted into the url.

Untold_Fact: The package name is inspired from the Vadachennai(2018) movie character Rajan, who's primary job is "Hooku adikiradhu".
'''

# specify requirements of your package here 
REQUIREMENTS = ['requests', 'bs4'] 
  
# some more details 
CLASSIFIERS = [ 
    'Development Status :: 4 - Beta', 
    'Intended Audience :: Developers', 
    'Topic :: Internet', 
    'License :: OSI Approved :: MIT License', 
    'Programming Language :: Python', 
    'Programming Language :: Python :: 2', 
    'Programming Language :: Python :: 2.6', 
    'Programming Language :: Python :: 2.7', 
    'Programming Language :: Python :: 3', 
    'Programming Language :: Python :: 3.3', 
    'Programming Language :: Python :: 3.4', 
    'Programming Language :: Python :: 3.5', 
    ] 
  
# calling the setup function  
setup(name='hooku', 
      version='1.0', 
      description='A script with webscraping utilites on a specific website', 
      long_description=long_description, 
      url='https://github.com/poomani98/Hooku', 
      author='Poomani K', 
      author_email='poomani98@gmail.com', 
      license='MIT', 
      packages=['hooku'], 
      classifiers=CLASSIFIERS, 
      install_requires=REQUIREMENTS, 
      keywords='web scrape primapad.com'
      ) 

