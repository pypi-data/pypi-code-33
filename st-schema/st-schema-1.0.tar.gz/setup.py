from setuptools import setup, find_packages

import os

setup(name='st-schema',
      version='1.0',
      description='SmartThings Schema helper library for python.',
      long_description='none',
      long_description_content_type="text/markdown",
      url='https://github.com/SmartThingsCommunity/st-schema-python',
      download_url='https://github.com/SmartThingsCommunity/st-schema-python/archive/stschema-1.0.tar.gz',
      author='SmartThings',
      author_email='juan@smartthings.com',
      license='Apache License 2.0',
      entry_points={},
      classifiers=[
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 3 - Alpha',

          # Indicate who your project is intended for
          'Intended Audience :: Developers',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',

          # Pick your license as you wish (should match "license" above)
          'License :: OSI Approved :: Apache Software License',

          # Specify the Python versions you support here. In particular, ensure
          # that you indicate whether you support Python 2, Python 3 or both.

          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
      keywords='smartthings schema cloud c2c st',

      packages=find_packages(exclude=(['tests', 'docs', 'site', 'env'])),
      )
