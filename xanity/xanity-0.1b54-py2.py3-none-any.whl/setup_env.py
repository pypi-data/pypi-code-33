#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Barry Muldrey
#
# This file is part of xanity.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import os
import subprocess
import pkg_resources
import sys
import inspect
import shutil
import tempfile
from fnmatch import fnmatch
from shlex import split as shsplit

from . import xanity


helptext ="""
setup an existing xanity directory tree

usage:  xanity setup [help]

xanity setup assumes you're in a xanity tree
"""

env_spec_filepath = 'conda_environment.yaml'

# get the full path to this file :
thispath = os.path.abspath(os.path.realpath(os.path.split(inspect.stack()[0][1])[0]))


def setup(project_root):
    # ported from bash

    # # if project doesn't have a UUID make one:
    # uuid_file = os.path.join(project_root, '.xanity', 'UUID')
    # if not os.path.isfile(uuid_file):
    #     uuid = os.path.split(project_root)[-1] + '_' + "".join(choice(string.ascii_letters) for x in range(4))
    #     open(uuid_file, mode='w').writelines(uuid + '\n')
    # else:
    #     uuid = str(open(uuid_file, mode='r').read()).strip()

    # check for 'conda_environment.yaml' file
    if not os.path.isfile(os.path.join(project_root, env_spec_filepath)):
        print('could not find {} which contains the desired conda environment.  Please make one.\n\n')
        print(
            "example {} file:\n\n"
            "    name: < my-env-name >         "
            "    channels:                     "
            "      - javascript                "
            "    dependencies:                 "
            "      - python=3.4                "
            "      - bokeh=0.9.2               "
            "      - numpy=1.9.*               "
            "      - nodejs=0.10.*             "
            "      - flask                     "
            "      - pip:                      "
            "        - Flask-Testing           "
            "        - \"--editable=git+ssh://git@gitlab.com/lars-gatech/pyspectre.git#egg=pyspectre\""
            "        - \"git+ssh://git@gitlab.com/lars-gatech/libpsf.git#egg=libpsf\""
            "".format(env_spec_filepath, env_spec_filepath)
        )
        raise SystemExit(1)

    else:
        print("found environment file: {}".format(env_spec_filepath))

    conda_env_path = os.path.join(project_root, '.xanity', 'conda_env')

    # if conda env exists:
    if os.path.isfile(os.path.join(conda_env_path, 'bin', 'python')):

        # update conda env
        subprocess.check_call([
            'bash', '-lc', 'conda env update --file {} -p {}'.format(env_spec_filepath, conda_env_path)
        ])
        print('updated conda env at {}'.format(conda_env_path))

    else:

        # create conda env
        subprocess.check_call([
            'bash', '-lc', 'conda env create --file {} -p {}'.format(env_spec_filepath, conda_env_path)
        ])
        print('created conda env at {}'.format(conda_env_path))

    # get xanity version
    xanityver = pkg_resources.require("xanity")[0].version
    print('installing (-e) your base xanity into the new env'.format(xanityver))

    # link source:
    try:
        os.mkdir(os.path.join(thispath, 'self_replication'))
    except OSError:
        pass

    # subprocess.check_call(shsplit(
    #     'rm -rf {}/self_replication'.format(thispath)
    # ))
    shutil.rmtree(os.path.join(thispath, 'self_replication'))

    ignore = ['*.egg-info', '.eggs', 'self_replication', '__pycache__', '*~', 'setup.py', '*.pyc']

    for based, subds, files in os.walk(os.path.join(thispath)):
        # don't go into ignored dirs
        if any([fnmatch(based, item) for item in ignore]):
            continue

        for subd in subds:
            if not any([fnmatch(subd, item) for item in ignore]):
                try:
                    relpath = os.path.join(based, subd).split(thispath)[1].lstrip(os.sep)
                    os.makedirs(os.path.join(thispath, 'self_replication', 'xanity', relpath))
                except OSError:
                    pass

        for afile in files:
            if not any([fnmatch(afile, item) for item in ignore]):
                relpath = os.path.join(based, afile).split(thispath)[1].lstrip(os.sep)

                s = os.path.join(based, afile)
                d = os.path.join(thispath, 'self_replication', 'xanity', relpath)

                os.symlink(s, d)
                # do not make hardlinks... will confuse editors!!!
                # subprocess.check_call(shsplit(
                #     'ln -sf {} {}'.format(os.path.join(based, afile), os.path.join(thispath, 'self_replication', 'xanity', relpath))
                # ))

    subprocess.check_call(shsplit(
        'bash -lc \'conda activate {} && pip install -U -e {}\''.format(
            conda_env_path, thispath)
    ))

    # open(os.path.join(project_root, '.xanity', 'setupcomplete'), mode='w').write('')

    return 0


def main():
    dirspec = xanity.args.directory

    if dirspec == 'help':
        print(helptext)
        raise SystemExit(1)

    # print(
    #     "#####################################\n"
    #     "##          xanity setup           ##\n"
    #     "#####################################\n"
    # )

    if not dirspec:
        dirspec = xanity.project_root

    dirspec = os.path.expandvars(os.path.expanduser(dirspec))

    if os.path.isdir(dirspec):
        if os.path.isdir(os.path.join(dirspec, '.xanity')):
            project_root = dirspec

        else:
            print('Specified directory doesn\'t seem to be a xanity project. Try running \'xanity init\'')
    else:
        print('Specified directory does not exist')
        # project_root = os.path.abspath(os.path.join(os.getcwd(), dirspec))

    opwd = os.getcwd()

    os.chdir(project_root)

    if not os.path.isfile(os.path.join(xanity.conf_files.conda_env, 'bin', 'python')):
        # result = subprocess.call(['bash', setup_script, project_root])
        result = setup(project_root)
        if result == 0:
            xanity._freeze_conda()

    else:
        print('environment exists. checking status...')
        if not xanity._check_conda():
            print('updating environment...')
            # result = subprocess.call(['bash', setup_script, project_root])
            result = setup(project_root)
            if result == 0:
                xanity._freeze_conda()
        else:
            print('looks like current setup is valid')

    os.chdir(opwd)


if __name__ == "__main__":
    main()
