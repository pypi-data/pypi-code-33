from setuptools import setup
from pysimplehttpdownloader.metadata import Metadata

metadata = Metadata()


def requirements():
    """Build the requirements list for this project"""
    requirements_list = []

    with open('requirements.txt') as requirements:
        for install in requirements:
            requirements_list.append(install.strip())

    return requirements_list

long_description = """

pySimpleHTTPDownloader (shttpd)
-------------------------------

Simple HTTP downloader written in Python

Installation
~~~~~~~~~~~~

You can install or upgrade shttpd with:

``$ pip install shttpd --upgrade``

Or you can install from source with:

.. code:: bash

   $ git clone https://github.com/RDCH106/pySimpleHTTPDownloader.git --recursive
   $ cd pysimplehttpdownloader
   $ pip install .

Quick example
~~~~~~~~~~~~~

.. code:: bash

   $ shttpd -u https://raw.githubusercontent.com/RDCH106/i-love-firefox/183266a9/I_Love_Firefox_220x56.png

The example downloads ``I_Love_Firefox_220x56.png`` in current path and
shows download progress.

Help
~~~~

Run the following command to see all options available:

``shttpd --help`` or ``shttpd -h``
    """


setup(
    name = 'shttpd',
    packages = ['pysimplehttpdownloader'],
    install_requires = requirements(),
    version = metadata.get_version(),
    license = 'LGPL v3',
    description = 'Simple HTTP downloader written in Python',
    long_description= long_description,
    author = metadata.get_author(),
    author_email = 'contact@rdch106.hol.es',
    url = 'https://github.com/RDCH106/pySimpleHTTPDownloader',
    download_url = 'https://github.com/RDCH106/pySimpleHTTPDownloader/archive/v'+metadata.get_version()+'.tar.gz',
    entry_points={
        'console_scripts': ['shttpd=pysimplehttpdownloader.main:main'],
    },
    keywords = 'http downloader',
    classifiers = ['Programming Language :: Python',
                   'Programming Language :: Python :: 3.2',
                   'Programming Language :: Python :: 3.3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6'],
)