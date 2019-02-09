import os
from setuptools import setup, find_packages

dir_path = os.path.dirname(os.path.realpath(__file__))

VERSION = open(os.path.join(dir_path, 'VERSION')).read()


setup(
  name = 'nice-oom-daemon',
  packages = find_packages(),
  version = VERSION,
  description = '''
  A daemon for docker which sends signals to containers when they hit their memory soft limit.
  ''',
  long_description=open(os.path.join(dir_path, 'README.md')).read(),
  long_description_content_type='text/markdown',
  author = 'Marco Montagna',
  author_email = 'marcojoemontagna@gmail.com',
  url = 'https://github.com/mmontagna/nice-oom-daemon',
  keywords = [],
  classifiers=(
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'Natural Language :: English',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python',
      'Programming Language :: Python :: 2',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.6',
  ),
  data_files = [('', ['LICENSE', 'VERSION', 'README.md'])],
  include_package_data=True,
  python_requires=">=2.7",
  license=open(os.path.join(dir_path, 'LICENSE')).read(),
  install_requires=[
    "simplejson>=3.8.0",
    "docker"
  ],
  entry_points = {
    'console_scripts': [
      'nice-oom-daemon = nice_oom.__main__:main',
    ],
  },
)