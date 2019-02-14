from distutils.core import setup
setup(
  name = 'venmosplit',
  packages = ['venmosplit'], 
  version = '0.6',
  description = 'Split the tab the right way',
  author = 'Nicholas Fix',
  author_email = 'njfix6@gmail.com',
  url = 'https://github.com/njfix6/venmo-split.git',
  download_url = 'https://github.com/njfix6/venmo-split.git/archive/0.2.tar.gz',
  keywords = ['venmo'],
  classifiers = [],
  entry_points = {
        'console_scripts': ['venmosplit=venmosplit.venmosplit:main']
        },
)