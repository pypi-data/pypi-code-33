from distutils.core import setup
setup(
  name = 'lod-executor',
  packages = ['lod_executor',],
  version = '1.0.36',
  description = 'A program for executing other programs on behalf of elody.com',
  long_description = 'A program for executing other programs on behalf of elody.com',
  author = 'Florian Dietz',
  author_email = 'floriandietz44@gmail.com',
  url='https://elody.com',
  license = 'MIT',
  package_data={
      '': ['*.txt', # this covers both the LICENSE.txt file in this folder, and the TRUTH.txt file in the /lod/ folder
            '*.cnf',
        ],
   },
   entry_points = {
        'console_scripts': [
            'lod-executor=lod_executor.executor:main',
        ],
    },
    install_requires=[
        'bottle==0.12.13',
        'cheroot==5.9.1',
        'docker==3.7.0',
        'python-dateutil==2.6.1',
        'pyOpenSSL==17.5.0',
        'requests_toolbelt==0.8.0',
    ],
)
