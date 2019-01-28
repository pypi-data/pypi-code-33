from setuptools import setup

setup(
	name = 'innoreg',
	version = '0.1',
	author = 'Philippe Kappel',
	author_email = 'philippe.kappel@gmail.com',
	description = 'Inno Setup Registry',
	url = 'http://phyl.io/?page=innoreg.html',
	packages = ['innoreg'],
	package_data = {'': ['*.islu', 'logo.bmp']},
	entry_points = {'console_scripts': ['innoreg = innoreg:main']},
	classifiers = [
		'Development Status :: 3 - Alpha',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'Intended Audience :: End Users/Desktop',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved :: MIT License',
		'Natural Language :: English',
		'Natural Language :: French',
		'Operating System :: Microsoft :: Windows',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
		'Programming Language :: Python :: 3.8',
		'Topic :: Software Development :: Code Generators',
		'Topic :: Utilities'
	]
)