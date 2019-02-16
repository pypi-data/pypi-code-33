#!/usr/bin/env python
"""
X Library
-------------
Framework to handle simplify development application with,
flask, consulate and sql alchemy together
"""

import sys

from setuptools import setup, find_packages

# Dependencies:

if sys.version_info[0] == 2:
	dnspython = 'dnspython'
elif sys.version_info[0] == 3:
	dnspython = 'dnspython3'
else:
	raise ValueError('Unsupported python version')

INSTALL_REQUIRES = [
	'consulate',
	'Flask',
	'Flask-SQLAlchemy',
	'Flask-Caching',
	'dnspython',
	'kafka-python'
]

TESTS_REQUIRE = [
	'mock',
	'six',
	'coverage',
	'pytest',
]

setup(
	name='x-lib',
	version='0.0.7',
	license='Apache',
	author='Rifky Aditya Bastara',
	author_email='kiditzbastara@gmail.com',
	
	description='Flask library to easy configuration',
	long_description=__doc__,
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	platforms='any',
	install_requires=INSTALL_REQUIRES,
	tests_require=TESTS_REQUIRE,
	extras_require={
		'test': TESTS_REQUIRE,
	},
	test_suite='tests',
	
	classifiers=[
		'Development Status :: 2 - Pre-Alpha',
		'Environment :: Web Environment',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: Apache Software License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
		'Topic :: Software Development :: Libraries :: Python Modules'
	],
	entry_points={
		'console_scripts': [
			'api-generator = backend.apigen:main',
			'testgen = backend.testgen:main',
			'service-generator = backend.service_generator:main'
		],
	}
)
