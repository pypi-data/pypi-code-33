from setuptools import setup

setup(
	name = 'mkey',
	version = '0.2',
	description = 'Mouse and Key',
	url = 'http://phyl.io/?page=mkey.html',
	author = 'Philippe Kappel',
	author_email = 'philippe.kappel@gmail.com',
	license = 'MIT',
	long_description = "`mkey` is an [AutoHotkey](https://www.autohotkey.com) script generator with a short syntax to automate tasks such as double-click, write a sentense, run delayed commands in a terminal, open a web page and connect with a login and a password.",
	long_description_content_type = 'text/markdown',
	keywords = 'AutoHotkey',
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
		'Topic :: Utilities'],
	packages = ['mkey'],
	package_data = {'': ['header.ahk']},
	entry_points = {'console_scripts': ['mkey = mkey:main']}
)