import pkgutil
import importlib
from distutils.core import setup

import os
import sys
import save_to_db
print(save_to_db.__file__)
sys.path.insert(0, os.path.dirname(save_to_db.__file__))


packages = []
def add_package(package_load_path):
    global packages
    packages.append(package_load_path)
    package = importlib.import_module(package_load_path)
    for _, modname, ispkg in pkgutil.iter_modules(package.__path__):
        if not ispkg:
            continue
        add_package('{}.{}'.format(package_load_path, modname))
add_package('save_to_db')

def readme():
    with open('README.rst') as fp:
        return fp.read()

setup(
    name = 'Save-to-DB',
    packages = packages,
    version = '0.2.1a',
    description = ('Make it easy to store data from any source into a '
                   'database.'),
    long_description = readme(),
    author = 'Mikhail Aleksandrovich Makovenko',
    author_email = 'mma86@rambler.ru',
    url = 'https://bitbucket.org/mikhail-makovenko/save-to-db',
    download_url = \
        'https://bitbucket.org/mikhail-makovenko/save-to-db/get/0.2.1a.tar.gz',
    keywords = 'development scraping mining database',
    license = 'MIT',
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
    ],
)
