import os
import sys

import setuptools
from setuptools.command.test import test as TestCommand
import subprocess


tests_require = ['pytest',
                 'pytest-asyncio']

requires = ['ruamel.yaml',
            'aiohttp',
            'jinja2',
            'plac',
            'plyer',
            'tinydb']

# Get plac from git until the interactive mode fix is released downstream
plac = ['https://github.com/micheles/plac/tarball/master#egg=plac-0.9.6']


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ''

    def run_tests(self):
        import shlex
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


def get_mo_files():
    """
    Compile the *.po trainslation files.
    """
    po_dir = 'vigil/locale'
    po_path = 'LC_MESSAGES/vigil.po'
    po_files = [os.path.join(f, po_path) for f in os.listdir(
        po_dir) if os.path.splitext(f)[1] != '.pot']
    for po_file in po_files:
        po_file = os.path.join(po_dir, po_file)
        mo_file = '{}.mo'.format(os.path.splitext(po_file)[0])
        msgfmt_cmd = 'msgfmt {} -o {}'.format(po_file, mo_file)
        subprocess.call(msgfmt_cmd, shell=True)
    return 'locale/*/*/*.mo'


setuptools.setup(
    name="vigil-cli",
    version="0.3",
    description="Automatically monitor websites for changes",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Radek Sprta",
    author_email="mail@radeksprta.eu",
    url="http://www.gitlab.com/radek-sprta/vigil",
    download_url="https://gitlab.com/radek-sprta/vigil/repository/archive.tar.gz?ref=master",
    packages=setuptools.find_packages(),
    package_data={'vigil': ['config/*.yaml', get_mo_files(), 'templates/*.j2'],
                  'tests': ['data/*']},
    install_requires=requires,
    dependency_links=plac,
    tests_require=tests_require,
    cmdclass={'test': PyTest},
    entry_points={
        'console_scripts': [
            'vigil = vigil.__main__:main',
        ],
    },
    classifiers=[
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Communications :: Email",
        "Topic :: Utilities"] + [
        ('Programming Language :: Python :: %s' % x) for x in
        '3 3.6 3.7'.split()
    ]
)
