from setuptools import setup 
  

# Package meta-data.
NAME = 'inotimake'
DESCRIPTION = ''
URL = 'https://github.com/a77763/inoti-make'
EMAIL = 'pachedo@gmail.com'
AUTHOR = 'A77763'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '1.0.0'



# reading long description from file 
with open('DESCRIPTION.txt') as file: 
    long_description = file.read() 
  
  
# specify requirements of your package here 
REQUIREMENTS = ['json', 'os', 'subprocess', 'shlex', 'sys', 'nltk', 're'] 
  
# some more details 
CLASSIFIERS = [ 
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: Implementation :: PyPy'
    ] 
  
# calling the setup function  
setup(
    name=NAME,
    version='1.0.0',
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=['inotimake'], 
    classifiers=CLASSIFIERS, 
    install_requires=REQUIREMENTS, 
      ) 
