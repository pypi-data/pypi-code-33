from setuptools import setup, Extension
from os import path
from io import open

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


neoscrypt_module = Extension('neoscrypt',
                             sources=['src/neoscryptmodule.c',
                                      'src/neoscrypt.c'],
                             include_dirs=['.', 'src'])

setup(name='neoscrypt',
      version='1.2.1',
      description='Bindings for the NeoScrypt proof-of-work algorithm',
      author='z3r0 m0r4k',
      author_email='mor4k@outlook.com',
      url='https://github.com/sparkspay/python-neoscrypt',
      ext_modules=[neoscrypt_module],
      zip_safe=True,
      long_description=long_description,
      long_description_content_type='text/markdown',
      )
