from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='emailFahad',
      version='0.3',
      description='Travel Email Parser for lola',
      long_description=readme(),
      classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='email trip booking parser',
      author='Lola',
      author_email='fahadshawal@gmail.com',
      license='MIT',
      packages=['trip-email-parser'],
      dependency_links=['https://pip.aws.lolatravel.com/pip/dev/+f/558/7ae71d33ab3f9/lola.utils-2.4.21.tar.gz'],
      install_requires=[
        'beautifulsoup4==4.6.0',
	'html5lib==0.99999',
	'python-dateutil==2.4.2',
	'decorator==4.0.2',
	'docutils==0.12',
	'enum34==1.1.2',
	'google-api-python-client==1.6.2',
	'injector==0.9.1',
	'numpy==1.11.0',
	'peewee==2.8.0',
	'python-dateutil==2.4.2',
	'regex==2016.06.24',
	'requests==2.11.0',
	'schematics==2.0.0.dev2',
	'ujson==1.35',
	'urllib3==1.15.1',
	'phonenumbers==8.7.1',
	'python-googlegeocoder==0.3.0',
	'redis==2.10.6',
	'fuzzywuzzy==0.16.0',
	],
	entry_points={
          'console_scripts': ['runner_file=runner:main'],
      },
      include_package_data=True,
      zip_safe=False)

