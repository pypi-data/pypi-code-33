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
import os.path as path
import shutil
import pkg_resources
import subprocess
from random import choice, randint
import string
import sys

from . import xanity

helptext = '''
        initialize a new xanity directory tree, or reset an existing tree
        (will not overwrite)

        usage:  xanity init [path] [help]

        if path is provided, xanity tree will be created there
        if path is not provided, xanity tree will be created in the pwd
        '''

exclude_list = [
    r'"__pycache__"',
    r'"*~"',
]


def main():
    if xanity.args.directory:
        dirspec = xanity.args.directory
    elif xanity.unknownargs:
        dirspec = xanity.unknownargs[0]
    else:
        dirspec = ''

    if dirspec == 'help':
        print(helptext)
        raise SystemExit(1)

    # print(
    #     "#####################################\n"
    #     "##            xanity init          ##\n"
    #     "#####################################\n"
    # )

    if not dirspec:
        dirspec = str(os.getcwd())

    dirspec = path.expandvars(path.expanduser(dirspec))
    if os.path.isdir(dirspec):
        project_root = os.path.abspath(dirspec)
        print('Initializing xanity inside existing directory: {}'.format(project_root))

    else:
        project_root = os.path.abspath(os.path.join(os.getcwd(), dirspec))
        print('Creating a new xanity project directory: {}'.format(project_root))

    if not xanity.args.examples:
        exclude_list.extend([r'"*_EXAMPLE"'])
    else:
        print('and including examples')

    skel_root = pkg_resources.resource_filename(__name__, 'skeleton')

    rsync_cmd = ['rsync', '-rz', '--ignore-existing', skel_root + os.sep, project_root + os.sep]
    rsync_cmd.extend(['--exclude={}'.format(item) for item in exclude_list])

    subprocess.call(rsync_cmd)

    if xanity.args.examples:
        # walk tree and rename _EXAMPLE files
        for base, dirs, files in os.walk(project_root):
            for item in dirs+files:

                if item.endswith('_EXAMPLE'):

                    redundancy = os.path.join(base, item.split('_EXAMPLE')[0])
                    example_path = os.path.join(base, item)

                    if item in files:
                        try:
                            os.remove(redundancy)
                        except OSError:
                            pass

                    elif item in dirs:
                        try:
                            shutil.rmtree(redundancy)
                        except Exception:
                            pass

                    os.rename(example_path, redundancy)

    else:
        # walk tree and remove any _EXAMPLE files lingering:
        del_list = []
        for base, dirs, files in os.walk(project_root):
            for item in dirs+files:
                if item in dirs:
                    type='d'
                elif item in files:
                    type='f'
                if item.endswith('_EXAMPLE'):
                    del_list.append((os.path.join(base, item), type))

        for item, type in del_list:
            if type == 'f':
                os.remove(item)
            elif type == 'd':
                try:
                    shutil.rmtree(item)
                except:
                    pass

    uuid_file = os.path.join(project_root, '.xanity', 'UUID')

    if not os.path.isfile(uuid_file):
        uuid = os.path.split(project_root)[-1] + '_' + "".join(choice(string.ascii_letters) for x in range(4))
        open(uuid_file, mode='w').writelines(uuid+'\n')

    opwd = os.getcwd()
    os.chdir(project_root)
    git_subroutine(project_root)
    os.chdir(opwd)


def git_subroutine(project_root):
    # print(
    #     "#####################################\n"
    #     "##               git               ##\n"
    #     "#####################################\n"
    # )

    gi_pak = path.join(project_root, '.gitignore-deploy')
    gi_exist = path.join(project_root, '.gitignore')

    if (path.isfile(gi_exist)):
        print('found existing .gitignore. NOT clobbering it')
        os.remove(gi_pak)

    #        # check ages
    #        gi_pak_age = os.stat(gi_pak).st_mtime
    #        gi_exist_age =  os.stat(gi_exist).st_mtime
    #    
    #        # overwrite existing
    #        os.remove(gi_exist)
    #            
    else:
        os.rename(gi_pak, gi_exist)
        print('deployed xanity\'s .gitignore')

    # initialize a git repo
    if not subprocess.call(['bash', '-c', 'type -t git'], stdout=open('/dev/null', 'w'), stderr=subprocess.STDOUT):
        # git is working 
        if not subprocess.call(['git', 'status'], stdout=open('/dev/null', 'w'), stderr=subprocess.STDOUT):
            # it is a git repo already
            print('leaving existing Git repo alone...')
        else:

            try:
                result = subprocess.check_output(['git', 'init', project_root])
                print("successfully created a new git repo...")
            except Exception as e:
                print("could not create new git repo")
                print("[debug:] git output: {}".format(e.message))
                raise SystemExit

            if not b'Reinitialized existing Git repository' in result:
                # nothing went wrong

                try:
                    subprocess.check_call(['git', 'add', '-A'])
                    print('\nmade an initial commit to your new repo')
                except Exception:
                    print("xanity was unable to add files to git")
                    raise SystemExit

                try:
                    subprocess.check_call(['git', 'commit', '-am', 'xanity initial commit'], stdout=open('/dev/null', 'w'), stderr=subprocess.STDOUT)
                    print('Files committed to new git repo. Use \'git status\' to see whats up\n')
                except Exception:
                    print("xanity was unable to commit to the new git repo")
                    raise SystemExit

            else:
                print("xanity may have accidentally reset your git repo. "
                      "Try git ref-log and the web for help :P. sorry.")
                raise SystemExit


if __name__ == "__main__":
    main()
