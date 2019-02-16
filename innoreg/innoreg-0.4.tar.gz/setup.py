from setuptools import setup

description = '''\
`innoreg` customize Windows Registry.

Dependencies
------------

* [Python](https://www.python.org) 3.6+
* [Inno Setup](http://jrsoftware.org/isinfo.php) 5u, 6 — *chosen against* [NSIS](https://nsis.sourceforge.io/Main_Page) *for its DPI scaling support*
* [ExecTI](https://winaero.com/comment.php?comment.news.1843) — *optional, for highest permissions*'''

setup(
	name = 'innoreg',
	version = '0.4',
	description = 'Inno Setup Registry',
	url = 'http://phyl.io/?page=innoreg.html',
	author = 'Philippe Kappel',
	author_email = 'philippe.kappel@gmail.com',
	license = 'MIT',
	long_description = description,
	long_description_content_type = 'text/markdown',
	keywords = 'Inno',
	classifiers = [
		'Development Status :: 4 - Beta',
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