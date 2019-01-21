"""

keyup :  Copyright 2017-2018, Blake Huber

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

see: https://www.gnu.org/licenses/#GPL

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
contained in the program LICENSE file.

"""

import os
import sys
import platform
import subprocess
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from codecs import open
from shutil import copy2 as copyfile
from shutil import rmtree
import keyup


requires = [
    'awscli>=1.16.1',
    'boto3>=1.9.1',
    'PyYAML',
    'Pygments>=2.2.0',
    'pyaws>=0.2.26',
    'pytz>=2018.3',
    'tqdm>=4.26.0',
    'veryprettytable>=0.8.1'
]


_root = os.path.abspath(os.path.dirname(__file__))
_comp_fname = 'keyup-completion.bash'


def _root_user():
    """
    Checks localhost root or sudo access
    """
    if os.geteuid() == 0:
        return True
    elif subprocess.getoutput('echo $EUID') == '0':
        return True
    return False


def create_artifact(object_path, type):
    """Creates post install filesystem artifacts"""
    if type == 'file':
        with open(object_path, 'w') as f1:
            f1.write(sourcefile_content())
    elif type == 'dir':
        os.makedirs(object_path)


def os_parityPath(path):
    """
    Converts unix paths to correct windows equivalents.
    Unix native paths remain unchanged (no effect)
    """
    path = os.path.normpath(os.path.expanduser(path))
    if path.startswith('\\'):
        return 'C:' + path
    return path


class PostInstallDevelop(develop):
    """ post-install, development """
    def run(self):
        subprocess.check_call("bash scripts/post-install-dev.sh".split())
        develop.run(self)


class PostInstall(install):
    """
    Summary.

        Postinstall script to place bash completion artifacts
        on local filesystem

    """
    def run(self):
        completion_file = user_home() + '/.bash_completion'
        completion_dir = user_home() + '/.bash_completion.d'
        config_dir = user_home() + '/.config/keyup'

        if not os.path.exists(os_parityPath(completion_file)):
            create_artifact(os_parityPath(completion_file), 'file')
        if not os.path.exists(os_parityPath(completion_dir)):
            create_artifact(os_parityPath(completion_dir), 'dir')
        if not os.path.exists(os_parityPath(config_dir)):
            create_artifact(os_parityPath(config_dir), 'dir')
        if _root_user():
            copyfile(
                    completion_dir + '/' + _comp_fname,
                    '/etc/bash_completion.d/' + _comp_fname,
                )
            os.remove(completion_dir + '/' + _comp_fname)
        install.run(self)


def preclean(dst):
    if os.path.exists(dst):
        os.remove(dst)
    return True


def read(fname):
    basedir = os.path.dirname(sys.argv[0])
    return open(os.path.join(basedir, fname)).read()


def sourcefile_content():
    sourcefile = """
    for bcfile in ~/.bash_completion.d/* ; do
        [ -f "$bcfile" ] && . $bcfile
    done\n
    """
    return sourcefile


def user_home():
    """Returns os specific home dir for current user"""
    try:
        if platform.system() == 'Linux':
            return os.getenv('HOME')

        elif platform.system() == 'Windows':
            username = os.getenv('username')
            return 'C:\\Users\\' + username

        elif platform.system() == 'Java':
            print(f'Unsupported of {os_type}')
            sys.exit(1)
    except OSError as e:
        raise e


setup(
    name='keyup',
    version=keyup.__version__,
    description='Automated IAM Access Key Rotation for Amazon Web Services',
    long_description=read('DESCRIPTION.rst'),
    url='http://keyup.readthedocs.io',
    author=keyup.__author__,
    author_email=keyup.__email__,
    license='GPL-3.0',
    classifiers=[
        'Topic :: Security',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows'
    ],
    keywords='Amazon Web Services iam credentials AWS access key secret key',
    packages=find_packages(exclude=['docs', 'scripts', 'assets']),
    include_package_data=True,
    install_requires=requires,
    python_requires='>=3.5, <4',
    cmdclass={
        'install': PostInstall
    },
    data_files=[
        (user_home() + '/' + '.bash_completion.d', ['bash/' + _comp_fname]),
        (user_home() + '/' + '.config/keyup', ['bash/iam_users.py'])
    ],
    entry_points={
        'console_scripts': [
            'keyup=keyup.cli:init_cli',
            'keyconfig=keyup.keyconfig:option_configure'
        ]
    },
    zip_safe=False
)
