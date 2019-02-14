from setuptools import setup, find_packages
version = "2.1.0"
setup(
  name="e3db",
  version=version,
  packages=find_packages(),
  install_requires=[
    'PyNaCl >= 1.3.0, < 2',
    'requests >= 2.19.1, < 3',
    'Cryptography >= 2.2',
  ],
  url = "https://github.com/tozny/e3db-python",
  download_url = 'https://github.com/tozny/e3db-python/archive/{0}.tar.gz'.format(version),
  description  = open("README.md").read(),
  author = "Tozny, LLC",
  author_email = "info@tozny.com",
  license = open("LICENSE.md").read(),
  keywords = ['e3db', 'encryption', 'encrypted-store'],
  classifiers = [],
)
