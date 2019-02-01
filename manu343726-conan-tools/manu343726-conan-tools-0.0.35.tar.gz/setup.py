from distutils.core import setup
import os

VERSION=os.environ.get('CONAN_TOOLS_VERSION', '0.0.35')

setup(
  name = 'manu343726-conan-tools',
  packages = ['manu343726_conan_tools'],
  install_requires = [
    'future'
  ],
  version = VERSION,
  description = 'Miscellaneous tools for development of conan.io recipes',
  author = 'Manu Sanchez',
  author_email = 'Manu343726@gmail.com',
  url = 'https://gitlab.com/Manu343726/conan-tools',
  download_url = 'https://gitlab.com/Manu343726/conan-tools/-/archive/v{version}/conan-tools-v{version}.tar.gz'.format(version=VERSION),
  keywords = ['conan'],
  entry_points={
    'console_scripts': [
        'manu343726-conan-tools=manu343726_conan_tools.main:main'
    ]
  },
  classifiers=[
    'Development Status :: 1 - Planning',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6'
  ],
)
