"""
Holds the configuration information for this software
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='app-utilities',
      packages=['app_util'],
      version='0.1.9',
      description='A utility to fast-track application configurations',
      author='Philip Whiting',
      author_email='phwhitin@cisco.com',
      url='https://github.com/Himself12794/app-utilities',
      download_url='https://github.com/Himself12794/app-utilities/archive/v0.1.9.tar.gz',
      keywords=['configuration', 'utility'],
      install_requires=['pymongo>=3.0.0', 'requests>=2.0.0']
     )
