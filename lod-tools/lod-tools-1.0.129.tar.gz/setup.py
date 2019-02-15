from distutils.core import setup
setup(
  name = 'lod-tools',
  packages = ['lod_tools',],
  version = '1.0.129',
  description = 'A program for interacting with the API of elody.com',
  long_description = 'A program for interacting with the API of elody.com',
  author = 'Florian Dietz',
  author_email = 'floriandietz44@gmail.com',
  url='https://elody.com',
  license = 'MIT',
  package_data={
      '': ['*.txt', # this covers both the LICENSE.txt file in this folder, and the TRUTH.txt file in the /lod/ folder
          'program_example/*', # this covers the data in the Docker program example folder
          'input_example/*'], # this covers the data in the input example folder
   },
   entry_points = {
        'console_scripts': [
            'lod-tools=lod_tools.lod_tools:main',
        ],
    },
    install_requires=[
        'docker==3.7.0',
    ],
)
