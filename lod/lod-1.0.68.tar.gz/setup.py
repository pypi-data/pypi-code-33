from distutils.core import setup
setup(
  name = 'lod',
  packages = ['lod'],
  version = '1.0.68',
  description = 'A library containing basic code useful when creating Docker Images for elody.com',
  long_description = 'A library containing basic code useful when creating Docker Images for elody.com',
  author = 'Florian Dietz',
  author_email = 'floriandietz44@gmail.com',
  url='https://elody.com',
  license = 'MIT',
  package_data={
      '': ['*.txt'], # this covers both the LICENSE.txt file in this folder, and the TRUTH.txt file in the /lod/ folder
   },
   install_requires=[
       'six==1.11.0',
   ],
)
