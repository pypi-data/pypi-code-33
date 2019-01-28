from setuptools import setup

setup(
	name = 'mkey',
	version = '0.1',
	author = 'Philippe Kappel',
	author_email = 'philippe.kappel@gmail.com',
	description = 'Mouse and Key',
	url = 'http://phyl.io/?page=mkey.html',
	packages = ['mkey'],
	package_data = {'': ['header.ahk']},
	entry_points = {'console_scripts': ['mkey = mkey:main']},
	classifiers = [
		'Development Status :: 3 - Alpha',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'Intended Audience :: End Users/Desktop',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved :: MIT License',
		'Natural Language :: English',
		'Operating System :: Microsoft :: Windows',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
		'Programming Language :: Python :: 3.8',
		'Topic :: Software Development :: Code Generators',
		'Topic :: Utilities'
	]
)