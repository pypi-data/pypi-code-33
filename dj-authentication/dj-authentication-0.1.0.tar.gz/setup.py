from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding = 'utf-8') as f:
	long_description = f.read()

setup(
	name = 'dj-authentication',
	version = '0.1.0',
	description = 'Nice HTTP authentication support for Django',
	long_description = long_description,
	long_description_content_type = 'text/markdown',
	url = 'https://gitlab.com/aiakos/dj-authentication',
	author = 'Aiakos Contributors',
	author_email = "aiakos@aiakosauth.com",
	classifiers = [
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'Topic :: System :: Systems Administration :: Authentication/Directory',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
		'Framework :: Django',
		'Framework :: Django :: 2.0',
		'Framework :: Django :: 2.1',
	],
	keywords = 'http auth authentication basic www-authenticate',
	packages = find_packages(exclude = ['contrib', 'docs', 'tests']),
	zip_safe = True,
	install_requires = ['django>=2.0.0'],
)
