from setuptools import setup, find_packages


setup(
  name                 = 'Chronologer',
  version              = '0.3.2',
  author               = 'saaj',
  author_email         = 'mail@saaj.me',
  test_suite           = 'chronologer.test',
  license              = 'GPL-3.0',
  url                  = 'https://bitbucket.org/saaj/chronologer/src/backend',
  description          = 'Python HTTP logging server',
  long_description     = open('README.rst').read(),
  platforms            = ['Any'],
  packages             = find_packages(),
  package_data         = {'chronologer': ['migration/*.py']},
  classifiers = [
    'Topic :: Database',
    'Framework :: CherryPy',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: Implementation :: CPython',
    'Intended Audience :: Developers'
  ],
  extras_require = {
    'server' : [
      'cherrypy < 9',
      'clor < 0.3',
      'yoyo-migrations < 6',
      'schedule < 0.6',
      'python-sql < 2',
      'rules < 3',
      'brotli < 2',
      'pytz'
    ],
    'mysql' : ['mysqlclient >= 1.3.11, < 1.4'],
    'ui'    : ['chronologerui >= 0.3, < 0.4'],
  },
)

