import codecs
import os
import sys

try:
	from setuptools import setup
except:
	from distutils.core import setup



def read(fname):
	return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

long_des = read("README.rst")
    
platforms = ['linux/Windows']
classifiers = [
    'Development Status :: 3 - Alpha',
    'Topic :: Text Processing',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',
]

install_requires = [
    # 'numpy>=1.11.1',
    # 'pandas>=0.19.0'
    'requests'
]

    
setup(name='benyo_zbx',
      version='0.0.8',
      description='A zabbix api for pypi',
      long_description=long_des,
      author = "Benyo yuan", 
      packages=['benyo_zbx'],
      author_email = "yuyuhupo@outlook.com" ,
      url = "https://benyo.github.io" ,
      license="Apache License, Version 2.0",
      platforms=platforms,
      classifiers=classifiers,
      install_requires=install_requires,
      include_package_data=True 
      )   
      
