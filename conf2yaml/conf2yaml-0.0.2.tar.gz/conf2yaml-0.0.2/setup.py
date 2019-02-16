from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
	long_description = f.read()

setup(
	name='conf2yaml',
	version='0.0.2',
	description="It's a Network configuration parser, which translates the show outputs",
	long_description = long_description,
	long_description_content_type = 'text/markdown',
	url = 'https://github.com/network-tools/conf2yaml',
	author = 'Kiran Kumar Kotari, Shameer Ali M',
	author_email='kotarikirankumar@gmail.com, ali.shameer@gmail.com',
	classifiers = [ 
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Developers',
		'Topic :: Software Development :: Build Tools',
		'License :: OSI Approved :: MIT License', 
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3.1',
		'Programming Language :: Python :: 3.2',
		'Programming Language :: Python :: 3.3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
		],
	keywords = 'network conf parser translator cisco show output parser',
	packages = find_packages(exclude=['tests', 'data', 'asserts']),
)
