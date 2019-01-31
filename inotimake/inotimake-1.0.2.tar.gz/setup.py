from setuptools import setup 
  

# Package meta-data.
NAME = 'inotimake'
DESCRIPTION = ''
URL = 'https://github.com/a77763/inoti-make'
EMAIL = 'pachedo@gmail.com'
AUTHOR = 'A77763'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '1.0.0'


  
# specify requirements of your package here 
REQUIREMENTS = ['os', 'subprocess', 'shlex', 'sys', 'nltk', 're'] 
  
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
    version='1.0.2',
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=['inotimake'], 
    classifiers=CLASSIFIERS, 
    install_requires=REQUIREMENTS, 
      ) 
