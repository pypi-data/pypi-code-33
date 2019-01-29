from setuptools import setup

setup(
	name = 'innoreg',
	version = '0.2',
	description = 'Inno Setup Registry',
	url = 'http://phyl.io/?page=innoreg.html',
	author = 'Philippe Kappel',
	author_email = 'philippe.kappel@gmail.com',
	license = 'MIT',
	long_description = "`innoreg` is an executable generator that allows to customize Windows Registry with a syntax shorter than `*.reg` files, the `reg` command and PowerShell's `*-ItemProperty`.",
	long_description_content_type = 'text/markdown',
	keywords = 'Inno',
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
		'Topic :: Utilities'],
	packages = ['innoreg'],
	package_data = {'': ['*.islu', 'logo.bmp']},
	entry_points = {'console_scripts': ['innoreg = innoreg:main']}
)