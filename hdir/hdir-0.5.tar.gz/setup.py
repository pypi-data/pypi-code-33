from setuptools import setup

description = '''\
`hdir()` is a highlighted version of the `dir()` function.

Dependencies
------------

* [Python](https://www.python.org) 3.6+
* Console with [ANSI colors](https://en.wikipedia.org/wiki/ANSI_escape_code)'''

setup(
	name = 'hdir',
	version = '0.5',
	description = 'Highlight dir',
	url = 'http://phyl.io/?page=hdir.html',
	author = 'Philippe Kappel',
	author_email = 'philippe.kappel@gmail.com',
	license = 'MIT',
	long_description = description,
	long_description_content_type = 'text/markdown',
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved :: MIT License',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
		'Programming Language :: Python :: 3.8',
		'Topic :: Software Development',
		'Topic :: Utilities'],
	packages = ['hdir'],
	install_requires = ['ansiwrap']
)