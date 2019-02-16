from setuptools import setup

description = '''\
`aunt` automates Windows installation with
[AutoUnattend.xml](https://docs.microsoft.com/en-us/windows-hardware/manufacture/desktop/automate-windows-setup)
and reduces [image](https://msdn.microsoft.com/en-us/library/windows/desktop/dd861280.aspx) size.

Dependencies
------------

* [Python](https://www.python.org) 3.6+
* [7-Zip](https://www.7-zip.org)
* [Oscdimg](http://phyl.io/oscdimg.exe) — *add to Path*'''

setup(
	name = 'aunt',
	version = '0.1',
	description = 'Auto Unattend',
	url = 'http://phyl.io/?page=aunt.html',
	author = 'Philippe Kappel',
	author_email = 'philippe.kappel@gmail.com',
	license = 'MIT',
	long_description = description,
	long_description_content_type = 'text/markdown',
	keywords = 'Autounattend',
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
	packages = ['aunt'],
	entry_points = {'console_scripts': ['aunt = aunt:main']}
)