#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © %YEAR%  <>
#
# Distributed under terms of the %LICENSE% license.

"""
Tool for easy push project to pypi and binstar (Anaconda).
Git pull, bumpversion, pip build and upload, conda build and upload and git push is performed.
There is also option to init new project directory.

"""

import logging

logger = logging.getLogger(__name__)
import argparse
import subprocess
import os
import os.path as op
import shutil
import glob


def mycall(command):
    if type(command) is list:
        subprocess.call(command)
    else:
        subprocess.call(command, shell=True)

def check_git():
    try:
        import git
        import git.exc
    except:
        logger.info("GitPython is not installed")
        return

    try:
        repo = git.Repo(".")
    except git.exc.InvalidGitRepositoryError as e:
        logger.info("It is not Git repo")


    if repo.is_dirty():
        logger.error("Git working directory is dirty. Clean it.")
        exit()

def make(args):
    if op.exists("meta.yaml"):
        # old position of recipe
        prefix = "conda-recipe/"
    else:
        prefix = ""

    if not op.exists("conda-recipe"):
        import os
        os.makedirs("conda-recipe")
    if not op.exists(prefix + "build.sh"):
        with open(prefix + 'build.sh', 'a') as the_file:
            the_file.write('#!/bin/bash\n\n$PYTHON setup.py install\n')
    if not op.exists(prefix + "bld.bat"):
        with open(prefix + 'bld.bat', 'a') as the_file:
            the_file.write('"%PYTHON%" setup.py install\nif errorlevel 1 exit 1')

    check_git()
    if (args.action == "init"):
        init(args) #, author=args.author, email=args.email, githubuser=args.gihubuser)
        return
    elif (args.action == "stable"):
        mycall("git push --tags")
        mycall("git checkout stable")
        mycall("git pull origin master")
        mycall("git push")
        mycall("git checkout master")
        return
    elif args.action in ["minor", "major", "patch"]:
        if args.skip_bumpversion:
            logger.info("skip bumpversion")
        else:
            logger.debug("pull, patch, push, push --tags")
            mycall("git pull")
            mycall("bumpversion " + args.action)
            mycall("git push")
            mycall("git push --tags")
        # if args.init_project_name is "pypi":
        #     upload_conda = False
    elif args.action in ["stay"]:
        logger.debug("stay on version")
    # elif args.action in ["build_conda"]:
    #     logger.debug("build conda based on meta.yaml")
    #     process_pypi = False
    elif args.action in ["skeleton"]:
        logger.debug("building skeleton")
        package_name = args.project_name
        mycall(["conda", "skeleton", "pypi", package_name])
        return
    else:
        logger.error("Unkown command '"+ args.action + "'")
        return

# fi
    # upload to pypi
    if not args.skip_pypi:
        pypi_build_and_upload(args)


    pythons = args.py
    if len(args.py) == 0 or (len(args.py) > 0 and args.py in ("both", "all")):
        pythons = ["2.7", "3.6"]
    logger.info("python versions " + str( args.py))

    for python_version in pythons:
        if not args.skip_conda:
            package_name = args.init_project_name
            if package_name is None:
                package_name = "."
            conda_build_and_upload(python_version, args.channel, package_name=package_name)


def pypi_build_and_upload(args):
    pypi_upload = True
    if args.skip_pypi:
        pypi_upload = False

    if pypi_upload:
        logger.info("pypi upload")
        # preregistration is no longer required
        # mycall(["python", "setup.py", "register", "-r", "pypi"])
        if args.skip_upload:
            cmd = ["python", "setup.py", "sdist", "-r", "pypi"]
        else:
            cmd = ["python", "setup.py", "sdist", "upload", "-r", "pypi"]
        mycall(cmd)

    # build conda and upload
    logger.debug("conda clean")

    dr = glob.glob("win-*")
    for onedir in dr:
        shutil.rmtree(onedir)
    dr = glob.glob("linux-*")
    for onedir in dr:
        shutil.rmtree(onedir)
    dr = glob.glob("osx-*")
    for onedir in dr:
        shutil.rmtree(onedir)

    # this fixes upload confilct
    dr = glob.glob("dist/*.tar.gz")
    for onefile in dr:
        os.remove(onefile)


def conda_build_and_upload(python_version, channels, package_name=None, skip_upload=False):
    if package_name is None:
        if op.exists("conda-recipe/meta.yaml"):
            package_name = "./conda-recipe/"
        else:
            package_name = "."

    logger.debug("conda build")
    logger.debug("build python_version :" + str( python_version))
    python_short_version = python_version[0] + python_version[2]

    # subprocess.call("conda build -c mjirik -c SimpleITK .", shell=True)
    conda_build_command = ["conda", "build", "--py", python_version,  package_name]
    for channel in channels:
        conda_build_command.append("-c")
        conda_build_command.append(channel[0])
    conda_build_command.append("--no-anaconda-upload")

    mycall(conda_build_command)
    conda_build_command.append("--output")
    # output_name_lines = subprocess.check_output(["conda", "build", "--python", python_version, "--output", "."])
    logger.debug(" ".join(conda_build_command))
    output_name_lines = subprocess.check_output(conda_build_command)
    # get last line of output
    output_name = output_name_lines.split("\n")[-2]
    logger.debug("build output file: " + output_name)
    cmd_convert = ["conda", "convert", "-p", "all", output_name]
    logger.debug(" ".join(cmd_convert))
    mycall(cmd_convert)

    if package_name == ".":
        package_name = ""

    if skip_upload:
        logger.info("skip upload conda")
    else:
        logger.debug("binstar upload")
        # it could be ".tar.gz" or ".tar.bz2"
        mycall("anaconda upload */*" + package_name + "*" + python_short_version + "*.tar.*z*")
        mycall(["anaconda", "upload", output_name])

    logger.debug("rm files")
    dr = glob.glob("win-*")
    for onedir in dr:
        shutil.rmtree(onedir)
    dr = glob.glob("linux-*")
    for onedir in dr:
        shutil.rmtree(onedir)
    dr = glob.glob("osx-*")
    for onedir in dr:
        shutil.rmtree(onedir)

def init(args):
    _SETUP_PY = """# Fallowing command is used to upload to pipy
#    python setup.py register sdist upload
from setuptools import setup, find_packages
# Always prefer setuptools over distutils
from os import path

here = path.abspath(path.dirname(__file__))
setup(
    name='{name}',
    description='{description}',
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version='0.0.0',
    url='https://github.com/{githublogin}/{name}',
    author='{author}',
    author_email='{email}',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Bio-Informatics',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: BSD License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # 'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.2',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords='{keywords}',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=["examples", "devel", 'dist',  'docs', 'tests*']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/technical.html#install-requires-vs-requirements-files
    install_requires=['numpy', 'conda'],
    # 'SimpleITK'],  # Removed becaouse of errors when pip is installing
    dependency_links=[],

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # package_data={{
    #     'sample': ['package_data.dat'],
    # }},

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages.
    # see
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # entry_points={{
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # }},
)
"""

    _SETUP_CFG = """
[bumpversion]
current_version = 0.0.0
files = setup.py conda-recipe/meta.yaml
commit = True
tag = True
tag_name = {new_version}

[nosetests]
attr = !interactive,!slow,!LAR
"""

    _META_YML = """package:
  name: {name}
  version: "0.0.0"

source:
# this is used for build from git hub
  git_rev: 0.0.0
  git_url: https://github.com/mjirik/{name}.git

# this is used for pypi
  # fn: io3d-1.0.30.tar.gz
  # url: https://pypi.python.org/packages/source/i/io3d/io3d-1.0.30.tar.gz
  # md5: a3ce512c4c97ac2410e6dcc96a801bd8
#  patches:
   # List any patch files here
   # - fix.patch

build:
  ignore_prefix_files:
    - devel
    - examples
  
  # noarch_python: True
  # preserve_egg_dir: True
  # entry_points:
    # Put any entry points (scripts to be generated automatically) here. The
    # syntax is module:function.  For example
    #
    # - {name} = {name}:main
    #
    # Would create an entry point called io3d that calls {name}.main()


  # If this is a new build for the same version, increment the build
  # number. If you do not include this key, it defaults to 0.
  # number: 1

requirements:
  build:
    - python
    - setuptools
    # - {{ pin_compatible('imma', max_pin='x.x') }}

  run:
    - python
    # - {{ pin_compatible('imma', max_pin='x.x') }}
    # - numpy
    # - pyqt 4.11.* # [not win]
    # - pyqt 4.12.2 # [win]

test:
  # Python imports
  imports:
    - {name}

  # commands:
    # You can put test commands to be run here.  Use this to test that the
    # entry points work.


  # You can also put a file called run_test.py in the recipe that will be run
  # at test time.

  # requires:
    # Put any additional test requirements here.  For example
    # - nose

about:
  home: https://github.com/mjirik/{name}
  license: BSD License
  summary: 'distribution to pypi and conda'

# See
# http://docs.continuum.io/conda/build.html for
# more information about meta.yaml
"""


    _CONDARC = """#!/bin/bash

$PYTHON setup.py install

# Add more build steps here, if they are necessary.

# See
# http://docs.continuum.io/conda/build.html
# for a list of environment variables that are set during the build process.
"""

    _TRAVIS_YML="""language: python
os: linux
# Ubuntu 14.04 Trusty support
sudo: required
# dist: trusty
# install new cmake
#addons:
#  apt:
#    packages:
#      - cmake
#    sources:
#      - kalakris-cmake
env:
    - CONDA_PYTHON_VERSION=2.7
    - CONDA_PYTHON_VERSION=3.6
virtualenv:
  system_site_packages: true
before_script:
    # GUI
    - "export DISPLAY=:99.0"
    - "sh -e /etc/init.d/xvfb start"
    - sleep 3 # give xvfb sume time to start

before_install:
    - sudo apt-get update
    - sudo apt-get install -qq cmake libinsighttoolkit3-dev libpng12-dev libgdcm2-dev

    # We do this conditionally because it saves us some downloading if the
    # version is the same.
    - if [[ "$CONDA_PYTHON_VERSION" == "2.7" ]]; then
        wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O miniconda.sh;
      else
        wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh;
      fi
#    - wget http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh -O miniconda.sh
#    - chmod +x miniconda.sh
#    - ./miniconda.sh -b
    - bash miniconda.sh -b -p $HOME/miniconda
    - export PATH="$HOME/miniconda/bin:$PATH"
    - hash -r
    - conda config --set always_yes yes --set changeps1 no
    - conda config --add channels mjirik
    - conda config --add channels conda-forge
    - conda update -q conda
    # Useful for debugging any issues with conda
    - conda info -a

# command to install dependencies
install:

    # - sudo apt-get install -qq $(< apt_requirements.txt)
    - conda create --yes -n travis pip nose coveralls python=$CONDA_PYTHON_VERSION
    - source activate travis
#    - Install dependencies
    - conda install --yes -c SimpleITK -c luispedro -c mjirik --file requirements_conda.txt
#    - pip install -r requirements_pip.txt
#    - "echo $LD_LIBRARY_PATH"
#    - "pip install -r requirements.txt"
#    - 'mkdir build'
#    - "cd build"
#    - "cmake .."
#    - "cmake --build ."
#    - "sudo make install"
#    - pip install .
#    - "cd .."
#    - 'echo "include /usr/local/lib" | sudo tee -a /etc/ld.so.conf'
#    - 'sudo ldconfig -v'
#    - conda list -e
#    - python -m io3d.datasets -l 3Dircadb1.1 jatra_5mm exp_small sliver_training_001 io3d_sample_data head volumetrie
# command to run tests
script: nosetests -v --with-coverage --cover-package={name}
after_success:
    - coveralls
"""
    project_name = args.project_name
    formated_setup = _SETUP_PY.format(
        name=project_name,
        description="",
        keywords="",
        author="",
        email="",
        githublogin=""
    )
    formated_travis = _TRAVIS_YML.format(name=project_name)
    formated_meta = _META_YML.format(name=project_name)
    if args.dry_run:
        print(formated_setup)
        print(formated_travis)
        print(formated_meta)
    else:

        if not op.exists(".condarc"):
            with open('.condarc', 'a') as the_file:
                the_file.write('channels:\n  - default\n#  - mjirik')
        if not op.exists("setup.py"):
            with open('setup.py', 'a') as the_file:
                the_file.write(formated_setup)
        if not op.exists("setup.cfg"):
            with open('setup.cfg', 'a') as the_file:
                the_file.write(_SETUP_CFG)
        if not op.exists("meta.yaml"):
            with open('meta.yaml', 'a') as the_file:
                the_file.write(formated_meta)
        if not op.exists(".travis.yml"):
            with open('.travis.yml', 'a') as the_file:
                the_file.write(formated_travis)


def main():
    logger = logging.getLogger()

    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    logger.addHandler(ch)

    # create file handler which logs even debug messages
    # fh = logging.FileHandler('log.txt')
    # fh.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(
    #     '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # fh.setFormatter(formatter)
    # logger.addHandler(fh)
    # logger.debug('start')

    # input parser
    parser = argparse.ArgumentParser(
        description=__doc__
    )
    parser.add_argument(
        "action",
        help="Available values are: 'init', 'stay', 'patch', 'minor', 'major' or 'stable'. "
            "Git pull is performed in the beginning. "
            "If 'init' is used the project directory with all necessary files is prepared and app quits. "
            "Version number will be increased with bumpversion if option 'patch', 'minor' and 'major' is used. "
            "Command 'stay' causes skipping of the bumpversion. Comands 'stay', 'patch', 'minor' and 'major' "
            "build PyPi and conda package and upload it to the server. The changes are then pushed to git."
        ,
        default=None)
    parser.add_argument(
        "project_name",
        nargs='?',
        help="project directory (with setup.py) or new project name if 'init' action is used",
        default="default_project")
    parser.add_argument("--py",
            # default="2.7",
            # default="both",
            action="append",
            default=[],
            # default="all",
            help="specify python version. '--py 2.7' or '--py both' for python 3.6 and 2.7. "
                 "Parameter can be used multiple times.")
    parser.add_argument(
        "-c", "--channel",
        nargs=1,
        action="append",
        help="Add conda channel. Can be used multiple times.",
        default=[])
    # parser.add_argument(
    #     "arg2",
    #     required=False,
    #     default=None)
    # parser.add_argument(
    #     '-i', '--inputfile',
    #     default=None,
    #     # required=True,
    #     help='input file'
    # )
    parser.add_argument(
        '-ll', '--loglevel', type=int, default=None,
        help='Debug level 0 to 100')

    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='Debug mode')
    parser.add_argument(
        '-sp', '--skip-pypi', action='store_true',
        help='Do not upload to pypi')
    parser.add_argument(
        '-sc', '--skip-conda', action='store_true',
        help='Do not process conda package')
    parser.add_argument(
        '-sb', '--skip-bumpversion', action='store_true',
        help='Do not build and upload pypi package')
    parser.add_argument(
        '-su', '--skip-upload', action='store_true',
        help='Do not upload to pypi and conda')
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Do not create any files in init')
    args = parser.parse_args()

    if args.loglevel is not None:
        ch.setLevel(args.loglevel)

    if args.debug:
        ch.setLevel(logging.DEBUG)

    # print(dir(args))
    make(args)


if __name__ == "__main__":
    main()

