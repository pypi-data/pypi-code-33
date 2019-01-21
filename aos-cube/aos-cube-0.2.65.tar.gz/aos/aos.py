#!/usr/bin/env python

# Copyright (c) 2016 aos Limited, All Rights Reserved
# SPDX-License-Identifier: Apache-2.0

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.

from __future__ import print_function
import argparse
import json
import filecmp
import traceback
import glob
import zipfile
import platform
import serial

from .util import *
from .repo import *
from serial.tools import miniterm
from serial.tools.list_ports import comports

def get_host_os():
    host_os = platform.system()
    if host_os == 'Windows':
        host_os = 'Win32'
    elif host_os == 'Linux':
        if platform.machine().endswith('64'):
            bit = '64'
        else:
            bit = '32'
        host_os += bit
    elif host_os == 'Darwin':
        host_os = 'OSX'
    else:
        host_os = None
    return host_os

def get_aos_url():
    """Figure out proper URL for downloading AliOS-Things."""
    if is_domestic():
        aos_url = 'https://gitee.com/alios-things/AliOS-Things.git'
    else:
        aos_url = 'https://github.com/alibaba/AliOS-Things.git'

    return aos_url

def cd_aos_root():
    original_dir = os.getcwd()
    host_os = get_host_os()
    if host_os == 'Win32':
        sys_root = re.compile(r'^[A-Z]{1}:\\$')
    else:
        sys_root = re.compile('^/$')
    while os.path.isdir('./kernel/rhino') == False:
        os.chdir('../')
        if sys_root.match(os.getcwd()):
            return 'fail', original_dir
    return 'success', original_dir

def which(program):
    if platform.system() == 'Windows' and program.endswith('.exe') == False:
        program += '.exe'

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None

def cmd_version_match(cmd, version):
    cmd = which(cmd)
    if cmd == None:
        return False
    if version == 'all':
        return True
    match = False
    try:
        ret = subprocess.check_output([cmd, '-v'], stderr=subprocess.STDOUT)
    except:
        return match
    lines = ret.split('\n')
    for line in lines:
        if version in line:
            match = True
            break;
    return match

def download_toolchains(downloads):
    tmp_dir = 'tmp_{0:02x}'.format(ord(os.urandom(1)))
    while os.path.isdir(tmp_dir):
        tmp_dir = 'tmp_{0:02x}'.format(ord(os.urandom(1)))
    try:
        os.mkdir(tmp_dir)
    except:
        print('download toolchains failed: unable to create a temp folder')
        return
    try:
        os.chdir(tmp_dir)
        for download in downloads:
            result = 0
            name, git_url, dst_dir = download
            print('toolchain {} missing, start download ...'.format(name))
            print(git_url + ' -> ' + dst_dir)
            result += subprocess.call(['git', 'clone', '--depth=1', git_url, name])
            if result > 0:
                print('git clone toolchain {} failed'.format(name))
                print('You can mannually try fix this problem by running:')
                print('    git clone {} {}'.format(git_url, name))
                print('    mv {0}/main {1} && rm -rf {0}'.format(name, dst_dir))
            src_dir = name + '/main'
            if os.path.exists(src_dir) == False:
                print('toolchain folder {} none exist'.format(src_dir))
                result += 1
            if result == 0:
                dst_dir = '../' + dst_dir
                if os.path.isfile(dst_dir) == True:
                    os.remove(dst_dir)
                if os.path.isdir(dst_dir) == True:
                    shutil.rmtree(dst_dir)
                if os.path.isdir(os.path.dirname(dst_dir)) == False:
                    os.makedirs(os.path.dirname(dst_dir))
                shutil.move(src_dir, dst_dir)
                print('download toolchain {} succeed'.format(name))
            else:
                print('download toolchain {} failed'.format(name))
    except:
        traceback.print_exc()
    finally:
        os.chdir('../')
    try:
        shutil.rmtree(tmp_dir)
    except:
        print("toolchain auto-install error: can not remove temp folder {}, please remove it manually".format(tmp_dir))
        pass

def is_specific_path(toolchain):
    try:
        if toolchain['path_specific']:
            return True
    except KeyError as exc:
        return False
    return False

def _install_toolchains(build_args):
    board = None
    host_os = get_host_os()
    if host_os == None:
        error('Unsupported Operating System!')

    #cd to aos root_dir
    ret, original_dir = cd_aos_root()
    if ret != 'success':
        error("not in AliOS-Things source code directory")

    #check config file to be enable this function (for backward compatability)
    autodownload_enable = False
    if os.path.exists('build/toolchain_autodownload.config'):
        try:
            with open('build/toolchain_autodownload.config') as file:
                if 'yes' in file.read(): autodownload_enable = True
        except:
            pass
    if autodownload_enable == False:
        if os.path.isdir(original_dir): os.chdir(original_dir)
        return

    for arg in build_args:
        if '@' not in arg:
            continue
        args = arg.split('@')
        board = args[1]
        break

    if not board:
        if os.path.isdir(original_dir): os.chdir(original_dir)
        return
    if os.path.isdir(os.path.join('board', board)) == False:
        error('Can not find board {}'.format(board))

    downloads = []
    from .constant import boards
    if board in boards:
        print('Check if required tools for {} exist'.format(board))
        for toolchain in boards[board]:
            name = toolchain['name']
            command = toolchain['command']
            version = toolchain['version']
            if is_specific_path(toolchain) is True:
                cmd_path = '{}/bin/{}'.format(toolchain['path'], command)
            else:
                cmd_path = '{}/{}/bin/{}'.format(toolchain['path'], host_os, command)
            if cmd_version_match(cmd_path, version) == True:
                continue
            if toolchain['use_global'] and cmd_version_match(command, version) == True:
                continue
            git_url = toolchain['{}_url'.format(host_os)]
            if git_url == '':
                continue
            if is_domestic() is False:
                git_url = git_url.replace('gitee', 'github')
                git_url = git_url.replace('alios-things', 'aliosthings')

            if is_specific_path(toolchain) is True:
                downloads.append([name, git_url, '{}'.format(toolchain['path'])])
            else:
                downloads.append([name, git_url, '{}/{}'.format(toolchain['path'], host_os)])
    if len(downloads): download_toolchains(downloads)

    if os.path.isdir(original_dir): os.chdir(original_dir)

def _run_make(arg_list):
    #install dependent toolchains
    _install_toolchains(sys.argv[2:])

    # check operating system
    host_os = get_host_os()
    if host_os == None:
        error('Unsupported Operating System!')

    #cd to aos root_dir
    ret, original_dir = cd_aos_root()
    if ret != 'success':
        error("not in AliOS-Things source code directory")

    make_cmds = {
        'Win32': 'cmd/win32/make.exe',
        'Linux64': 'cmd/linux64/make',
        'Linux32': 'cmd/linux32/make',
        'OSX': 'cmd/osx/make'
        }
    tools_dir = os.path.join(os.getcwd(), 'build').replace('\\', '/')
    make_cmd = os.path.join(tools_dir, make_cmds[host_os])

    # Run make command
    make_cmd_str = ' '.join([make_cmd, 'HOST_OS=' + host_os, 'TOOLS_ROOT=' + tools_dir] + list(arg_list))
    popen(make_cmd_str, shell=True, cwd=os.getcwd())
    if os.path.isdir(original_dir): os.chdir(original_dir)

def is_path_component(path):
    if not os.path.exists(path):
        return False

    for f in os.listdir(path):
        tmp_file = os.path.join(path, f)
        if os.path.isfile(tmp_file) and tmp_file.endswith('.mk') and os.path.basename(path) == f[:-3]:
            return True

    return False


def copy_directory(src_dir, dst_dir, sub_dir=False):
    if not os.path.exists(src_dir):
        return

    if os.path.exists(dst_dir):
        if sub_dir:
            dcmp = filecmp.dircmp(src_dir, dst_dir)
            if dcmp.left_only:
                order_dir = sorted(dcmp.left_only)
                for od in order_dir:
                    copy_directory(os.path.join(src_dir, od), os.path.join(dst_dir, od))
        return

    try:
        shutil.copytree(src_dir, dst_dir)
    except OSError as exc:  # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src_dir, dst_dir)
        else:
            raise


def restore_aos_sdk(aos_sdk_path):
    with cd(aos_sdk_path):
        with open(os.devnull, 'w') as DEVNULL:
            try:
                if sys.platform.startswith('win'):
                    subprocess.Popen([git_cmd, 'checkout', '-f'], stdout=DEVNULL, stderr=DEVNULL)
                else:
                    subprocess.Popen(['nohup', git_cmd, 'checkout', '-f'], stdout=DEVNULL, stderr=DEVNULL)

            except ProcessException:
                pass


def generate_aos_program(program_path, aos_sdk_path, template):
    if not(program_path and os.path.isdir(program_path) and aos_sdk_path and os.path.isdir(aos_sdk_path)):
        error("AliOS-Things code isn't exits!!!")

    comp_name = os.path.basename(program_path)
    template = template if template else 'helloworld'
    pd = Program(program_path)

    example_dir = os.path.join(aos_sdk_path, 'app/example')
    src = os.listdir(os.path.join(example_dir, template))
    for s in src:
        if os.path.isdir(s):
            copy_directory(os.path.join(example_dir, template, s), os.path.join(program_path, s), True)
        else:
            shutil.copy(os.path.join(example_dir, template, s), program_path)

    with open(os.path.join(program_path, comp_name + '.mk'), 'w') as fout:
        with open(os.path.join(program_path, template + '.mk'), 'r') as fin:
            for line in fin:
                if line.startswith('NAME :='):
                    line = 'NAME := ' + comp_name
                fout.write(line)
    os.remove(os.path.join(program_path, template + '.mk'))

    pd.set_cfg(REMOTE_PATH, os.path.join(Global.get_path().replace(os.path.sep, '/'), 'remote'))
    pd.set_cfg(OS_PATH, aos_sdk_path.replace(os.path.sep, '/'))
    copy_directory(os.path.join(aos_sdk_path, '.vscode'), os.path.join(program_path, '.vscode'))
    vscode_cfg_file = os.path.join(program_path, '.vscode', 'settings.json')
    if os.path.exists(vscode_cfg_file):
        with open(vscode_cfg_file, 'r+') as f:
            vscode_cfg = json.load(f)
            vscode_cfg['aliosStudio.isAosSource'] = False
            f.seek(0)
            f.truncate()
            json.dump(vscode_cfg, f, indent = 4)


def get_path_root(path):
    tpath = os.path.dirname(path)
    while tpath != path:
        path = tpath
        tpath = os.path.dirname(path)
    return tpath


# Subparser handling
parser = argparse.ArgumentParser(prog='aos',
                                 description="Code management tool for aos - https://code.aliyun.com/aos/aos\nversion %s\n\nUse 'aos <command> -h|--help' for detailed help.\nOnline manual and guide available at https://code.aliyun.com/aos/aos-cube" % ver,
                                 formatter_class=argparse.RawTextHelpFormatter)
subparsers = parser.add_subparsers(title="Commands", metavar="           ")
parser.add_argument("--version", action="store_true", dest="version", help="print version number and exit")
subcommands = {}


# Process handling
def subcommand(name, *args, **kwargs):
    def __subcommand(command):
        if not kwargs.get('description') and kwargs.get('help'):
            kwargs['description'] = kwargs['help']
        if not kwargs.get('formatter_class'):
            kwargs['formatter_class'] = argparse.RawDescriptionHelpFormatter

        subparser = subparsers.add_parser(name, **kwargs)
        subcommands[name] = subparser

        for arg in args:
            arg = dict(arg)
            opt = arg['name']
            del arg['name']

            if isinstance(opt, basestring):
                subparser.add_argument(opt, **arg)
            else:
                subparser.add_argument(*opt, **arg)

        subparser.add_argument("-v", "--verbose", action="store_true", dest="verbose", help="Verbose diagnostic output")
        subparser.add_argument("-vv", "--very_verbose", action="store_true", dest="very_verbose",
                               help="Very verbose diagnostic output")

        def thunk(parsed_args):
            argv = [arg['dest'] if 'dest' in arg else arg['name'] for arg in args]
            argv = [(arg if isinstance(arg, basestring) else arg[-1]).strip('-').replace('-', '_')
                    for arg in argv]
            argv = {arg: vars(parsed_args)[arg] for arg in argv
                    if vars(parsed_args)[arg] is not None}

            return command(**argv)

        subparser.set_defaults(command=thunk)
        return command

    return __subcommand


# Sub command: setup
@subcommand('setup',
            dict(name=['-d', '--dest-dir'], dest='dest_dir',
                 help='Destination dir'),
            dict(name=['-b', '--branch'], dest='branch',
                 help='Branch to checkout'),
            dict(name=['-m', '--board'], dest='board',
                 help='Board name'),
            dict(name=['-s', '--strip-sources'], dest='strip_sources', action='store_true',
                 help='Strip irrelevant part from sources: git history, other boards ...'),
            help='Setup AliOS Things sources tree (experimental)',
            description=(
                    "Setup AliOS Things sources tree\n"
                    ))
def setup(dest_dir='./', branch='master', board=None, strip_sources=False):
    """ Download sources to specific directory, allow to strip irrelevant part for board building. """

    source_dir = os.path.join(dest_dir, OS_NAME)
    if source_dir and os.path.isdir(os.path.join(source_dir, '.git')):
        action('AliOS-Things code has been download \"%s\"' % source_dir)
    elif source_dir and os.path.isdir(source_dir):
        action('%s existed ...' % source_dir)
    else:
        aos_url = get_aos_url()
        aos_url += '#' + branch
        try:
            add(aos_url, path=source_dir)
        except Exception as e:
            raise e

    if board and strip_sources:
        action('Board %s specified with --strip-sources ...' % board)
        _strip_sources(source_dir, board)

def _strip_sources(source_dir, board):
    """ Remove .git/, board/*, platform/mcu/* dirs from sources. """

    strip_list = ['/.git', '/.aos']
    board_arch = None

    # Get board arch family from board's makefile
    board_mk = os.path.join(source_dir, 'board', board, board + '.mk')
    if os.path.isfile(board_mk):
        with open(board_mk) as file:
            for board_arch in file.readlines():
                if 'HOST_MCU_FAMILY' in board_arch:
                    break

        regex_board_arch = r'^HOST_MCU_FAMILY\s*:?=\s*(.*)'
        match = re.match(regex_board_arch, board_arch)
        board_arch = match.group(1)
    else:
        error('Unknow board name %s!' % board)

    mcu_list = os.listdir(source_dir + '/platform/mcu')
    mcu_list.remove('include')
    mcu_list.remove(board_arch)
    mcu_list = [ os.path.join('/platform/mcu/', item) for item in mcu_list ]

    board_list = os.listdir(source_dir + '/board')
    board_list.remove(board)
    board_list = [ os.path.join('/board/', item) for item in board_list ]

    strip_list += mcu_list + board_list

    for item in strip_list:
        tmp_dir = os.path.join(source_dir + item)
        if os.path.isdir(tmp_dir):
            action('Removing dir: %s' % tmp_dir)
            shutil.rmtree(tmp_dir)
        elif os.path.isfile(tmp_dir):
            action('Removing file: %s' % tmp_dir)
            os.remove(tmp_dir)
        else:
            pass

# New command
@subcommand('new',
            dict(name='name', help='The program or component name'),
            dict(name=['-c', '--component'], action='store_true',
                 help='Force creation of an aos component. Default: auto.'),
            dict(name=['-t', '--template'], nargs='?',
                 help=''),
            dict(name='--scm', nargs='?',
                 help='Source control management. Currently supported: %s. Default: git' % ', '.join(
                     [s.name for s in scms.values()])),
            dict(name='--protocol', nargs='?',
                 help='Transport protocol when fetching the aos OS repository when creating new program. Supported: https, http, ssh, git. Default: inferred from URL.'),
            help='Create new aos program or component',
            description=(
                    "Create a new aos program (aos new helloworld) or component(aos new -c helloworld)\n"
                    "Supported source control management: git"))
def new(name, scm='git', component=False, template=None, protocol=None):
    global cwd_root

    d_type = 'component' if component else 'program'
    d_path = name if os.path.isabs(name) else os.path.abspath(name)

    if os.path.exists(d_path):
        p = Program(d_path)
        if (d_type == 'program' and not p.is_cwd) or (d_type == 'component' and Repo.isrepo(d_path)):
            error("A %s with name \"%s\" already exists." % (d_type, os.path.basename(d_path)), 1)

    if scm and scm != 'none':
        if os.path.isdir(d_path) and Repo.isrepo(d_path):
            repo = Repo.fromrepo(d_path)
            if repo.scm.name != scm:
                error("A repository already exists in \"%s\" based on %s. Please select a different name or location." %
                      (d_path, scm), 1)
        else:
            repo_scm = [s for s in scms.values() if s.name == scm.lower()]
            if not repo_scm:
                error(
                    "You have specified invalid source control management system\n"
                    "Please specify one of the following SCMs: %s" % ', '.join([s.name for s in scms.values()]), 1)
            repo_scm[0].init(d_path)

    if len(os.listdir(d_path)) > 1:
        warning("Directory \"%s\" is not empty." % d_path)

    action("Create new %s \"%s\" (%s)" % (d_type, d_path, scm))
    p = Program(d_path)
    if d_type == 'program':
        # This helps sub-commands to display relative paths to the created program
        # p.set_root()
        aos_os_url = get_aos_url()
        url = aos_os_url + '#master'
        d = 'aos'
        aos_sdk_path = Global().get_cfg(AOS_SDK_PATH)
        if aos_sdk_path and os.path.isdir(os.path.join(aos_sdk_path, '.git')):
            action('AliOS-Things code has been download \"%s\"' % aos_sdk_path)
        else:
            try:
                change_path = Global().get_path()
                with cd(change_path):
                    add(url, None, protocol=protocol, top=False)
            except Exception as e:
                if os.path.isdir(os.path.join(d_path, d)):
                    rmtree_readonly(os.path.join(d_path, d))
                raise e

        generate_aos_program(d_path, Global().get_cfg(AOS_SDK_PATH), template)

        p.set_cfg(PROGRAM_PATH, d_path.replace(os.path.sep, '/'))
        p.set_cfg(PATH_TYPE, 'program')

    else:
        p.unset_root(d_path)
        with cd(d_path):
            with open(os.path.join(d_path, name + '.mk'), 'w') as fm:
                makefile_content = 'NAME := %s\n$(NAME)_SOURCES := %s\n$(NAME)_COMPONENTS :=\n$(NAME)_INCLUDES := .\n' % (
                    name, name + '.c')
                fm.write(makefile_content)

            with open(os.path.join(d_path, name + '.c'), 'w') as fc:
                fc.write('//source code file\n')

            with open(os.path.join(d_path, name + '.h'), 'w') as fh:
                fh.write('//head file\n')

    action("Create %s \"%s\" success" % (d_type, d_path))


def print_component_status(format):
    cwd_type = Repo().pathtype()
    os_name = OS_NAME

    if cwd_type == 'program':
        pd = Program(os.getcwd())
        aos_path = pd.get_cfg(OS_PATH)
        aos_remote_components = get_aos_components(pd.get_cfg(REMOTE_PATH))
        os_name = 'aos'
    else:
        if os.path.isdir("kernel/rhino"):
            aos_path = os.getcwd()
        else:
            aos_path = Global().get_cfg(AOS_SDK_PATH)

    aos_local_components = get_aos_components(aos_path)
    if format == 'json':
        json_components_dict = {}

        if cwd_type == 'program':
            pd = Program(os.getcwd())
            with cd(pd.get_cfg(PROGRAM_PATH)):
                cube_add_components = None
                cube_remove_components = None
                with open(CUBE_MAKEFILE, 'r') as fin:
                    for line in fin:
                        if line.startswith('CUBE_ADD_COMPONENTS :='):
                            cube_add_components = re.split('\s+', line[23:].strip())

                        if line.startswith('CUBE_REMOVE_COMPONENTS :='):
                            cube_remove_components = re.split('\s+', line[26:].strip())

                for path, name in aos_remote_components.items():
                    cube_add = False
                    cube_remove = False

                    rel_path = os.path.dirname(relpath(pd.get_cfg(PROGRAM_PATH), path))
                    if cube_add_components and os.path.dirname(rel_path) in cube_add_components:
                        cube_add = True
                    if cube_remove_components and os.path.dirname(rel_path) in cube_remove_components:
                        cube_remove = True

                    json_components_dict[rel_path] = {'name': name, 'cube_add': cube_add, 'cube_remove': cube_remove}

                for path, name in aos_local_components.items():
                    cube_add = False
                    cube_remove = False

                    rel_aos_path = os.path.dirname(relpath(aos_path, path))
                    rel_path = os.path.join(os_name, rel_aos_path).replace(os.path.sep, '/')

                    if cube_add_components and rel_aos_path in cube_add_components:
                        cube_add = True
                    if cube_remove_components and rel_aos_path in cube_remove_components:
                        cube_remove = True

                    json_components_dict[rel_path] = {'name': name, 'cube_add': cube_add, 'cube_remove': cube_remove}
        else:
            cube_add = False
            cube_remove = False
            for path, name in aos_local_components.items():
                json_components_dict[os.path.dirname(relpath(os.path.dirname(aos_path), path))] = {'name': name, 'cube_add': cube_add, 'cube_remove': cube_remove}

        print(json.dumps(json_components_dict, indent=4, sort_keys=True))
    else:
        if cwd_type != 'program':
            print('\nCurrent directory isn\'t AliOS-Things program, list AOS_SDK_PATH components.')
        print("\n                                                      AliOS-Things COMPONENTS                ")
        print('|===================================================================================================================|')

        print('| %-30s | %-80s |' % ('NAME', 'LOCATION'))

        if cwd_type == 'program':
            program_path = Program(os.getcwd()).get_cfg(PROGRAM_PATH)
            for path, name in aos_remote_components.items():
                print('| %-30s | %-80s |' % (name, os.path.dirname(relpath(program_path, path))))
        for path, name in aos_local_components.items():
            print('| %-30s | %-80s |' % (name, os.path.dirname(relpath(os.path.dirname(aos_path), path))))

        print('|===================================================================================================================|')


# List command
@subcommand('ls',
            dict(name=['-c', '--component'], action='store_true',
                 help='List component information.'),
            dict(name=['-f', '--format'], nargs='?',
                 help='Format output json, xml and so on.'),
            help='List cube info, default components info',
            description=("List the aos cube information."))
def list_(component=False, format=None):
    print_component_status(format)


# Import command
@subcommand('import',
            dict(name='url', help='URL of the program'),
            dict(name='path', nargs='?', help='Destination name or path. Default: current directory.'),
            dict(name=['-I', '--ignore'], action='store_true', help='Ignore errors related to cloning and updating.'),
            dict(name='--depth', nargs='?',
                 help='Number of revisions to fetch from the remote repository. Default: all revisions.'),
            dict(name='--protocol', nargs='?',
                 help='Transport protocol for the source control management. Supported: https, http, ssh, git. Default: inferred from URL.'),
            help='Import program from URL',
            description=(
                    "Imports aos program and its dependencies from a source control based URL\n"
                    "(GitHub, Bitbucket, aos.org) into the current directory or specified\npath.\n"
                    "Use 'aos add <URL>' to add a component into an existing program."))
def import_(url, path=None, ignore=False, depth=None, protocol=None, top=True):
    global cwd_root

    if not Repo.isurl(url) and not os.path.exists(url):
        url = AOS_COMPONENT_BASE_URL + '/' + url + '.git'
    repo = Repo.fromurl(url, path)
    if top:
        p = Program(path)
        if p and not p.is_cwd:
            error(
                "Cannot import program in the specified location \"%s\" because it's already part of a program \"%s\".\n"
                "Please change your working directory to a different location or use \"aos add\" to import the URL as a component." % (
                    os.path.abspath(repo.path), p.name), 1)

    protocol = Program().get_cfg('PROTOCOL', protocol)

    if os.path.isdir(repo.path) and len(os.listdir(repo.path)) > 1 and is_path_component(repo.path):
        info("Directory \"%s\" is a component." % repo.path, 1)
        return True

    if repo.clone(repo.url, repo.path, rev=repo.rev, depth=depth, protocol=protocol):
        with cd(repo.path):
            Program(repo.path).set_root()
            try:
                if repo.rev and repo.getrev() != repo.rev:
                    repo.checkout(repo.rev, True)
            except ProcessException as e:
                err = "Unable to update \"%s\" to %s" % (repo.name, repo.revtype(repo.rev, True))
                if depth:
                    err = err + (
                            "\nThe --depth option might prevent fetching the whole revision tree and checking out %s." % (
                    repo.revtype(repo.rev, True)))
                warning(err)
                return False
    else:
        err = "Unable to clone repository (%s)" % url
        warning(err)
        return False

    if os.path.isdir(repo.path):
        repo.sync()

        if top:  # This helps sub-commands to display relative paths to the imported program
            cwd_root = repo.path

        with cd(repo.path):
            deploy(ignore=ignore, depth=depth, protocol=protocol, top=False)

    return True


def get_component_dependencies(makefile):
    dependencies = []
    if makefile and makefile.endswith('.mk') and os.path.isfile(makefile):
        with open(makefile) as fin:
            for line in fin:
                line = line.strip('\n')
                while line.endswith('\\'):
                    line = line[:-1] + next(fin).rstrip('\n')
                if '$(NAME)_COMPONENTS' in line and not line.strip().startswith('#'):
                    line = line[line.rfind('=') + 1:].strip()
                    components = re.split(r'\s+', line)
                    for co in components:
                        if co:
                            dependencies.append(co)
    return dependencies


def add_component_remote(base_url, scm, name, origin):
    is_local = add_component_local(name, origin, True)
    if not is_local:
        # clone from the same as name base url
        lib = Repo.fromurl(base_url + '/' + name + '.' + scm.name)
        is_import_success = import_(lib.fullurl, lib.path, True, None, None, False)
        if not is_import_success and base_url != AOS_COMPONENT_BASE_URL:
            # clone from aos component url
            lib = Repo.fromurl(AOS_COMPONENT_BASE_URL + '/' + name + '.' + scm.name)
            is_import_success = import_(lib.fullurl, lib.path, True, None, None, False)

        if not is_import_success:
            error('Component \"%s\" can\'t find in aos && %s && %s' % (name, base_url, AOS_COMPONENT_BASE_URL))

        lib.sync()

        ret_val = change_cube_makefile(lib.name, origin, True, False, True)
        dependencies = get_component_dependencies(os.path.join(lib.path, lib.name + '.mk'))
        for dep in dependencies:
            add_component_remote(lib.url[:lib.url.rfind('/')], lib.scm, dep, get_remote_identify(lib.name))

        out = ('Add remote component \"%s\" success' % lib.url) if ret_val else ('Add remote component \"%s\" fail' % lib.url)
        action(out)
        return ret_val
    else:
        action('Add local component \"%s\" success' % name)
    return True


def get_aos_components(aos_path):
    makefile_dict = {}
    if os.path.isdir(aos_path):
        for (dir_path, dir_names, file_names) in os.walk(aos_path):
            for f in file_names:
                if ('out' not in dir_path) and ('build' not in dir_path) and ('tools/codesync' not in dir_path) and f.endswith('.mk'):
                    makefile_dict[os.path.join(dir_path, f)] = f[:-3]
    else:
        error('Find components dir is empty!')

    aos_components_dict = {}
    for path, name in makefile_dict.items():
        with open(path, 'r') as f:
            s = f.read()
            component_name = re.findall('^\s*NAME\s*:?=\s*(\S+)\s*\n', s)
            if len(component_name) == 1:
                aos_components_dict[path.replace(os.path.sep, '/')] = component_name[0]

    return aos_components_dict


def get_remote_identify(name):
    return REMOTE_PATH + '/' + name


def get_local_identify(name):
    dir_name = name.replace('.', os.sep)
    pd = Program(os.getcwd())
    with cd(pd.get_cfg(OS_PATH)):
        if os.path.isfile(os.path.join(dir_name, os.path.basename(dir_name) + '.mk')):
            return dir_name.replace(os.sep, '/')

        aos_paths = os.listdir(os.getcwd())
        for path in aos_paths:
            if os.path.isfile(os.path.join(path, dir_name, os.path.basename(dir_name) + '.mk')):
                return os.path.join(path, dir_name).replace(os.sep, '/')

        aos_components = get_aos_components(pd.get_cfg(OS_PATH))
        for makefile, component in aos_components.items():
            if name == component:
                return os.path.dirname(relpath(pd.get_cfg(OS_PATH), makefile)).replace(os.sep, '/')
    return None


def get_component_identify(name, is_local):
    return get_local_identify(name) if is_local else get_remote_identify(name)


def change_cube_makefile(name, origin, is_add, is_local, is_recursive):
    pd = Program(os.getcwd())
    with cd(pd.get_cfg(PROGRAM_PATH)):
        try:
            with open(CUBE_MAKEFILE, 'r') as fin:
                identify = get_component_identify(name, is_local)
                if not identify:
                    return False

                index = -1
                cube_add_components = 'CUBE_ADD_COMPONENTS :='
                cube_remove_components = 'CUBE_REMOVE_COMPONENTS :='
                lines = []
                cube_modify = False
                for line in fin:
                    line = line.strip()
                    if line.startswith('CUBE_ADD_COMPONENTS :='):
                        cube_add_components = line
                        continue
                    if line.startswith('CUBE_REMOVE_COMPONENTS :='):
                        cube_remove_components = line
                        continue

                    if line.startswith('#'+identify+'='):
                        index = len(lines)
                    lines.append(line)

                if is_add:
                    if identify not in cube_add_components:
                        cube_add_components += ' ' + identify
                        cube_modify = True
                    if identify in cube_remove_components:
                        cube_remove_components = cube_remove_components.replace(identify, '')
                        cube_modify = True

                    if index < 0 and identify != origin:
                        line = '#'+identify+'='+origin
                        lines.append(line)
                        cube_modify = True
                else:
                    if identify not in cube_remove_components:
                        if index >= 0:
                            del lines[index]
                            cube_modify = True
                        else:
                            if not is_recursive:
                                cube_remove_components += ' ' + identify
                                cube_modify = True

                    if identify in cube_add_components:
                        cube_add_components = cube_add_components.replace(identify, '')
                        cube_modify = True
                with open(CUBE_MAKEFILE, 'w') as fout:
                    for line in lines:
                        fout.write(line + '\n')
                    fout.write(cube_add_components + '\n')
                    fout.write(cube_remove_components + '\n')

                if cube_modify:
                    pd.set_cfg(CUBE_MODIFY, '1')
        except (IOError, OSError):
            error('cube.mk isn\'t find current dir')

    return True


def add_component_local(name, origin, is_recursive):
    return change_cube_makefile(name, origin, True, True, is_recursive)


# Add component command
@subcommand('add',
            dict(name='name', help='The component name or URL of the component'),
            dict(name=['-I', '--ignore'], action='store_true', help='Ignore errors related to cloning and updating.'),
            dict(name='--depth', nargs='?',
                 help='Number of revisions to fetch from the remote repository. Default: all revisions.'),
            dict(name='--protocol', nargs='?',
                 help='Transport protocol for the source control management. Supported: https, http, ssh, git. Default: inferred from URL.'),
            help='Add component from AOS_SDK_PATH or URL',
            description=(
                    "Add AliOS-Things component from AOS_SDK_PATH(with dependencies) or GitHub URL(no dependencies) into an existing program.\n"
                    "Use 'aos new TARGET' to new as a program"))
def add(name, path=None, ignore=False, depth=None, protocol=None, top=True):
    cwd_type = Repo().pathtype()
    if Repo.isurl(name):

        lib = Repo.fromurl(name, path)
        if lib.name != OS_NAME and Repo().pathtype() != 'program':
            error('Add component must in AliOS-Things program directory')

        import_(lib.fullurl, lib.path, ignore=ignore, depth=depth, protocol=protocol, top=False)
        lib.sync()

        if lib.name != OS_NAME:
            ret_val = change_cube_makefile(lib.name, get_component_identify(lib.name, False), True, False, False)
            out = ('Add remote component \"%s\" success' % lib.url) if ret_val else ('Add remote component \"%s\" fail' % lib.url)
            action(out)
            dependencies = get_component_dependencies(os.path.join(lib.path, lib.name + '.mk'))
            for dep in dependencies:
                add_component_remote(lib.url[:lib.url.rfind('/')], lib.scm, dep, get_component_identify(lib.name, False))
    else:
        if cwd_type != 'program':
            error('Add component must in AliOS-Things program directory')
        ret_val = add_component_local(name, get_component_identify(name, True), False)
        out = ('Add local component \"%s\" success' % name) if ret_val else ('Add local component \"%s\" fail' % name)
        action(out)


def remove_component_remote(name, origin):
    is_local = get_component_identify(name, True)
    if is_local:
        change_cube_makefile(name, origin, False, True, True)
        out = ('Remove local component \"%s\" success' % name)
    else:
        ret_val = change_cube_makefile(name, origin, False, False, True)
        out = ('Remove remote component \"%s\" success' % name) if ret_val else ('Remove component \"%s\" fail' % name)
        if ret_val:
            pd = Program(os.getcwd())
            dependencies = get_component_dependencies(os.path.join(pd.get_cfg(REMOTE_PATH), name, name + '.mk'))
            for dep in dependencies:
                remove_component_remote(dep, get_component_identify(name, False))

    action(out)


# Remove component
@subcommand('rm',
            dict(name='name', help='Component name'),
            help='Remove component',
            description=(
                    "Remove specified component, its dependencies and references from the current\n"
                    "You can re-add the component from AOS_SDK_PATH or URL via 'aos add name>'."))
def remove(name):
    cwd_type = Repo().pathtype()
    if cwd_type != 'program':
        error('Remove component must in AliOS-Things program dir!')

    ret_val = change_cube_makefile(name, get_component_identify(name, True), False, True, False)
    if ret_val:
        out = ('Remove local component \"%s\" success' % name)
    else:
        ret_val = change_cube_makefile(name, get_component_identify(name, False), False, False, True)
        out = ('Remove remote component \"%s\" success' % name) if ret_val else ('Remove component \"%s\" fail' % name)
        if ret_val:
            pd = Program(os.getcwd())
            dependencies = get_component_dependencies(os.path.join(pd.get_cfg(REMOTE_PATH), name, name + '.mk'))
            for dep in dependencies:
                remove_component_remote(dep, get_component_identify(name, False))

    action(out)


# Deploy command
@subcommand('deploy',
            dict(name=['-I', '--ignore'], action='store_true', help='Ignore errors related to cloning and updating.'),
            dict(name='--depth', nargs='?',
                 help='Number of revisions to fetch from the remote repository. Default: all revisions.'),
            dict(name='--protocol', nargs='?',
                 help='Transport protocol for the source control management. Supported: https, http, ssh, git. Default: inferred from URL.'),
            help='Find and add missing components and source codes',
            description=(
                    "Import missing dependencies in an existing program or component.\n"
                    "Use 'aos import <URL>' and 'aos add <URL>' instead of cloning manually and\n"
                    "then running 'aos deploy'"))
def deploy(ignore=False, depth=None, protocol=None, top=True):
    repo = Repo.fromrepo()
    repo.ignores()

    for lib in repo.libs:
        if os.path.isdir(lib.path):
            if lib.check_repo():
                with cd(lib.path):
                    update(lib.rev, ignore=ignore, depth=depth, protocol=protocol, top=False)
        else:
            import_(lib.fullurl, lib.path, ignore=ignore, depth=depth, protocol=protocol, top=False)
            repo.ignore(relpath(repo.path, lib.path))


# Source command
@subcommand('codes',
            dict(name='name', help='Destination component name without suffix'),
            dict(name=['-I', '--ignore'], action='store_true', help='Ignore errors related to cloning and updating.'),
            dict(name='--depth', nargs='?',
                 help='Number of revisions to fetch from the remote repository. Default: all revisions.'),
            dict(name='--protocol', nargs='?',
                 help='Transport protocol for the source control management. Supported: https, http, ssh, git. Default: inferred from URL.'),
            help='Import the optional component from the remote repository',
            description=(
                    "Import optional component defined by .codes file.\n"
                    "name of the .codes file should be specified ."))
def codes(name, ignore=False, depth=None, protocol=None, top=True):
    repo = Repo.fromrepo()
    code = Repo.fromcode(os.path.join(os.getcwd(), name + '.codes'))

    if os.path.isdir(code.path):
        if code.check_repo():
            with cd(code.path):
                update(code.rev, ignore=ignore, depth=depth, protocol=protocol, top=False)
    else:
        import_(code.fullurl, code.path, ignore=ignore, depth=depth, protocol=protocol, top=False)
        print('>>>>', repo.path, code.path)
        repo.ignore(relpath(repo.path, code.path))


# Publish command
@subcommand('publish',
            dict(name=['-A', '--all'], dest='all_refs', action='store_true',
                 help='Publish all branches, including new ones. Default: push only the current branch.'),
            dict(name=['-M', '--message'], dest='msg', type=str, nargs='?',
                 help='Commit message. Default: prompts for commit message.'),
            help='Publish program or component',
            description=(
                    "Publishes the current program or component and all dependencies to their\nassociated remote repository URLs.\n"
                    "This command performs various consistency checks for local uncommitted changes\n"
                    "and unpublished revisions and encourages to commit/push them.\n"
                    "Online guide about collaboration is available at:\n"
                    "www.aos.com/collab_guide"))
def publish(all_refs=None, msg=None, top=True):
    if top:
        action("Checking for local modifications...")

    repo = Repo.fromrepo()
    if repo.is_local:
        error(
            "%s \"%s\" in \"%s\" with %s is a local repository.\nPlease associate it with a remote repository URL before attempting to publish.\n"
            "Read more about publishing local repositories here:\nhttps://code.aliyun.com/aos/aos-cube/#publishing-local-program-or-component" % (
            "Program" if top else "Library", repo.name, repo.path, repo.scm.name), 1)

    for lib in repo.libs:
        if lib.check_repo():
            with cd(lib.path):
                progress()
                publish(all_refs, msg=msg, top=False)

    sync(recursive=False)

    if repo.dirty():
        action("Uncommitted changes in %s \"%s\" in \"%s\"" % (repo.pathtype(repo.path), repo.name, repo.path))
        if msg:
            repo.commit(msg)
        else:
            raw_input('Press enter to commit and publish: ')
            repo.commit()

    try:
        outgoing = repo.outgoing()
        if outgoing > 0:
            action("Pushing local repository \"%s\" to remote \"%s\"" % (repo.name, repo.url))
            repo.publish(all_refs)
        else:
            if top:
                action("Nothing to publish to the remote repository (the source tree is unmodified)")
    except ProcessException as e:
        if e[0] != 1:
            raise e


# Update command
@subcommand('update',
            dict(name='rev', nargs='?', help='Revision, tag or branch'),
            dict(name=['-C', '--clean'], action='store_true',
                 help='Perform a clean update and discard all modified or untracked files. WARNING: This action cannot be undone. Use with caution.'),
            dict(name='--clean-files', action='store_true',
                 help='Remove any local ignored files. Requires \'--clean\'. WARNING: This will wipe all local uncommitted, untracked and ignored files. Use with extreme caution.'),
            dict(name='--clean-deps', action='store_true',
                 help='Remove any local libraries and also libraries containing uncommitted or unpublished changes. Requires \'--clean\'. WARNING: This action cannot be undone. Use with caution.'),
            dict(name=['-I', '--ignore'], action='store_true',
                 help='Ignore errors related to unpublished libraries, unpublished or uncommitted changes, and attempt to update from associated remote repository URLs.'),
            dict(name='--depth', nargs='?',
                 help='Number of revisions to fetch from the remote repository. Default: all revisions.'),
            dict(name='--protocol', nargs='?',
                 help='Transport protocol for the source control management. Supported: https, http, ssh, git. Default: inferred from URL.'),
            help='Update to branch, tag, revision or latest',
            description=(
                    "Updates the current program or component and its dependencies to specified\nbranch, tag or revision.\n"
                    "Alternatively fetches from associated remote repository URL and updates to the\n"
                    "latest revision in the current branch."))
def update(rev=None, clean=False, clean_files=False, clean_deps=False, ignore=False, top=True, depth=None,
           protocol=None):
    if top and clean:
        sync()

    cwd_type = Repo.pathtype(cwd_root)
    cwd_dest = "program" if cwd_type == "directory" else "component"

    repo = Repo.fromrepo()
    # A copy of repo containing the .lib layout before updating
    repo_orig = Repo.fromrepo()

    if top and not rev and repo.isdetached():
        error(
            "This %s is in detached HEAD state, and you won't be able to receive updates from the remote repository until you either checkout a branch or create a new one.\n"
            "You can checkout a branch using \"%s checkout <branch_name>\" command before running \"aos update\"." % (
            cwd_type, repo.scm.name), 1)

    if repo.is_local and not repo.rev:
        action("Skipping unpublished empty %s \"%s\"" % (
            cwd_type if top else cwd_dest,
            os.path.basename(repo.path) if top else relpath(cwd_root, repo.path)))
    else:
        # Fetch from remote repo
        action("Updating %s \"%s\" to %s" % (
            cwd_type if top else cwd_dest,
            os.path.basename(repo.path) if top else relpath(cwd_root, repo.path),
            repo.revtype(rev, True)))

        try:
            repo.update(rev, clean, clean_files, repo.is_local)
        except ProcessException as e:
            err = "Unable to update \"%s\" to %s" % (repo.name, repo.revtype(rev, True))
            if depth:
                err = err + (
                        "\nThe --depth option might prevent fetching the whole revision tree and checking out %s." % (
                repo.revtype(repo.rev, True)))
            if ignore:
                warning(err)
            else:
                error(err, e[0])

        repo.rm_untracked()
        if top and cwd_type == 'component':
            repo.sync()
            repo.write()

    # Compare component references (.lib) before and after update, and remove libraries that do not have references in the current revision
    for lib in repo_orig.libs:
        if not os.path.isfile(lib.lib) and os.path.isdir(
                lib.path):  # Library reference doesn't exist in the new revision. Will try to remove component to reproduce original structure
            gc = False
            with cd(lib.path):
                lib_repo = Repo.fromrepo(lib.path)
                gc, msg = lib_repo.can_update(clean, clean_deps)
            if gc:
                action("Remove component \"%s\" (obsolete)" % (relpath(cwd_root, lib.path)))
                rmtree_readonly(lib.path)
                repo.unignore(relpath(repo.path, lib.path))
            else:
                if ignore:
                    warning(msg)
                else:
                    error(msg, 1)

    # Reinitialize repo.libs() to reflect the component files after update
    repo.sync()

    # Recheck libraries as their urls might have changed
    for lib in repo.libs:
        if os.path.isdir(lib.path) and Repo.isrepo(lib.path):
            lib_repo = Repo.fromrepo(lib.path)
            if (not lib.is_local and not lib_repo.is_local and
                    formaturl(lib.url, 'https') != formaturl(lib_repo.url, 'https')):  # Repository URL has changed
                gc = False
                with cd(lib.path):
                    gc, msg = lib_repo.can_update(clean, clean_deps)
                if gc:
                    action(
                        "Remove component \"%s\" (changed URL). Will add from new URL." % (relpath(cwd_root, lib.path)))
                    rmtree_readonly(lib.path)
                    repo.unignore(relpath(repo.path, lib.path))
                else:
                    if ignore:
                        warning(msg)
                    else:
                        error(msg, 1)

    # Import missing repos and update to revs
    for lib in repo.libs:
        if not os.path.isdir(lib.path):
            import_(lib.fullurl, lib.path, ignore=ignore, depth=depth, protocol=protocol, top=False)
            repo.ignore(relpath(repo.path, lib.path))
        else:
            with cd(lib.path):
                update(lib.rev, clean=clean, clean_files=clean_files, clean_deps=clean_deps, ignore=ignore, top=False)


#    if top:
#        program = Program(repo.path)
#        program.set_root()
#        program.post_action()
#        if program.is_classic:
#            program.update_tools('.temp')


# Synch command
@subcommand('sync',
            help='Synchronize aos component references',
            description=(
                    "Synchronizes all component and dependency references (.component files) in the\n"
                    "current program or component.\n"
                    "Note that this will remove all invalid component references."))
def sync(recursive=True, keep_refs=False, top=True):
    if top and recursive:
        action("Synchronizing dependency references...")

    repo = Repo.fromrepo()
    repo.ignores()

    for lib in repo.libs:
        if os.path.isdir(lib.path):
            lib.check_repo()
            lib.sync()
            lib.write()
            repo.ignore(relpath(repo.path, lib.path))
            progress()
        else:
            if not keep_refs:
                action("Remove reference \"%s\" -> \"%s\"" % (lib.name, lib.fullurl))
                repo.remove(lib.lib)
                repo.unignore(relpath(repo.path, lib.path))

    for code in repo.codes:
        if os.path.isdir(code.path):
            code.check_repo()
            code.sync()
            code.write_codes()
            repo.ignore(relpath(repo.path, code.path))
            progress()

    for root, dirs, files in os.walk(repo.path):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        files[:] = [f for f in files if not f.startswith('.')]

        for d in list(dirs):
            if not Repo.isrepo(os.path.join(root, d)):
                continue

            lib = Repo.fromrepo(os.path.join(root, d))
            if os.path.isfile(lib.lib) or os.path.isfile(lib.code):
                dirs.remove(d)
                continue

            dirs.remove(d)
            lib.write()
            repo.ignore(relpath(repo.path, lib.path))
            repo.add(lib.lib)
            progress()

    repo.sync()

    if recursive:
        for lib in repo.libs:
            if lib.check_repo():
                with cd(lib.path):
                    sync(keep_refs=keep_refs, top=False)

    # Update the .lib reference in the parent repository
    cwd_type = Repo.pathtype(cwd_root)
    if top and cwd_type == "component":
        repo = Repo.fromrepo()
        repo.write()


# Command status for cross-SCM status of repositories
@subcommand('status',
            dict(name=['-I', '--ignore'], action='store_true', help='Ignore errors related to missing libraries.'),
            help='Show version control status\n\n',
            description=(
                    "Show uncommitted changes a program or component and its dependencies."))
def status_(ignore=False):
    repo = Repo.fromrepo()
    if repo.dirty():
        action("Status for \"%s\":" % repo.name)
        log(repo.status() + "\n")

    for lib in repo.libs:
        if lib.check_repo(ignore):
            with cd(lib.path):
                status_(ignore)

def make_build(make_args):
    # aos new program
    if os.path.isfile(os.path.join(os.getcwd(), Cfg.file)):
        pd = Program(os.getcwd())
        os_path = pd.get_cfg(OS_PATH)

        build_dir = ''
        out_path = ''
        is_build_dir = 'BUILD_DIR=' in make_args or os.environ.get('BUILD_DIR')
        if not is_build_dir:
            out_path = os.path.join(os.getcwd(), 'out').replace(os.path.sep, '/')
            build_dir = 'BUILD_DIR=' + out_path

        # cube_makefile = 'CUBE_MAKEFILE=' + os.path.join(pd.get_cfg(PROGRAM_PATH), CUBE_MAKEFILE).replace(os.path.sep, '/')
        app_dir = 'APPDIR=' + os.path.dirname(os.getcwd())

        with cd(os_path):
            cube_modify = pd.get_cfg(CUBE_MODIFY)
            if cube_modify == '1':
                _run_make(['-e', '-f build/Makefile', 'clean'])
                if build_dir:
                    shutil.rmtree(out_path, True)
                pd.set_cfg(CUBE_MODIFY, '0')
            _run_make(['-e', '-f build/Makefile', make_args, app_dir, build_dir])
    else:
        # aos source code
        _run_make(['-e', '-f build/Makefile', make_args])

def scons_build(args):
    if os.path.exists('ucube.py') == True:
        make_args = ['scons -j4 -f ucube.py']
    else:
        make_args = ['scons -j4 -f build/ucube.py']

    target_find = False

    for arg in args:
        if '@' in arg and not target_find:
            targets = arg.split('@')
            if len(targets) < 2:
                error('Must special app and board when build aos')

            app = 'APPLICATION='+targets[0]
            board = 'BOARD=' + targets[1]
            make_args.append(app)
            make_args.append(board)

            if len(targets) == 3:
                build_type = 'TYPE=' + targets[2]
                make_args.append(build_type)

            target_find = True
        elif arg.startswith('JOBS=') and arg.replace('JOBS=', '').isdigit() == True:
            jnum = arg.replace('JOBS=', '-j')
            make_args[0] = make_args[0].replace('-j4', jnum)
        else:
            make_args.append(arg)

    popen(' '.join(make_args), shell=True, cwd=os.getcwd())


def get_scons_enabled_boards():
    if os.path.exists("build/scons_enabled.py"):
        module_path = os.path.abspath(os.path.join('build'))
        sys.path.append(module_path)
        from scons_enabled import scons_enabled_boards
        return scons_enabled_boards
    else:
        return []

# Make command
@subcommand('make',
            help='Make aos program/component',
            description="Make aos program/component.")
def make():
    from .constant import ver
    log('aos-cube version: %s\n' %ver)

    # Get the make arguments
    args = sys.argv[2:]


    make_args = ' '.join(args)
    for arg in args:
        if '@' in arg:
            targets = arg.split('@')
            if len(targets) < 2:
                error('Must special app and board when build aos')

            board = targets[1]
            if board in get_scons_enabled_boards():
                scons_build(args)
            else:
                make_build(make_args)

            return
    #aos make clean go here
    make_build(make_args)


# scons make command
@subcommand('scons',
            help='Make aos program/component by scons',
            description="Make aos program/component by scons.")
def scons():
    # Get the make arguments
    args = sys.argv[2:]

    #install dependent toolchains
    _install_toolchains(args)

    scons_build(args)


# Make command
@subcommand('makelib',
            dict(name='path', nargs='?', help='Library directory path.'),
            dict(name=['-N', '--new'], dest='new', action='store_true', help='Create a library configure makefile .'),
            dict(name=['-r', '--arch'],
                 help='The arch for static library compiling. E.g. "Cortex-M3", "Cortex-M4", "Cortex-M4F", "ARM968E-S", "linux"'),
            help='Compile static library\n\n',
            description=(
                    "Compile static library."))
def makelib(path, arch=None, new=False):
    if new:
        root_dir = Program().path
        with open(os.path.join(root_dir, 'build/template.mk'), 'r') as f:
            content = f.read()
        with open(os.path.join(root_dir, path, os.path.basename(path) + '_src.mk'), 'w') as f:
            f.write(content.replace('template', os.path.basename(path)))
        return

    if arch:
        _run_make(['-e', 'LIB_DIR=' + path, 'TARGET_ARCH=' + arch, '-f build/aos_library_makefile.mk'])
        return

    host_arch = ['Cortex-M3', 'Cortex-M4', 'Cortex-M4F', 'ARM968E-S', 'linux']
    for arch in host_arch:
        _run_make(['-e', 'LIB_DIR=' + path, 'TARGET_ARCH=' + arch, '-f build/aos_library_makefile.mk'])


# Generic config command
@subcommand('config',
            dict(name='var', nargs='?', help='Variable name. E.g. "AOS_SDK_PATH"'),
            dict(name='value', nargs='?',
                 help='Value. Will show the currently set default value for a variable if not specified.'),
            dict(name=['-g', '--global'], dest='global_cfg', action='store_true',
                 help='Use global settings, not local'),
            dict(name=['-u', '--unset'], dest='unset', action='store_true', help='Unset the specified variable.'),
            dict(name=['-l', '--list'], dest='list_config', action='store_true', help='List aos tool configuration.'),
            help='Tool configuration\n\n',
            description=(
                    "Gets, sets or unsets aos tool configuration options.\n"
                    "Options can be global (via the --global switch) or local (per program)\n"
                    "Global options are always overridden by local/program options.\n"
                    "Currently supported options: aosder, protocol, depth, cache"))

def config_(var=None, value=None, global_cfg=False, unset=False, list_config=False):
    name = var
    var = str(var).upper()

    if list_config:
        g = Global()
        g_vars = g.list_cfg().items()
        action("Global config:")
        if g_vars:
            for v in g_vars:
                log("%s=%s\n" % (v[0], v[1]))
        else:
            log("No global configuration is set\n")
        log("\n")

        p = Program(os.getcwd())
        action("Local config (%s):" % p.path)
        if not p.is_cwd:
            p_vars = p.list_cfg().items()
            if p_vars:
                for v in p_vars:
                    log("%s=%s\n" % (v[0], v[1]))
            else:
                log("No local configuration is set\n")
        else:
            log("Couldn't find valid aos program in %s\n" % p.path)

    elif name:
        if global_cfg:
            # Global configuration
            g = Global()
            if unset:
                g.set_cfg(var, None)
                action('Unset global %s' % name)
            elif value:
                g.set_cfg(var, value)
                action('%s now set as global %s' % (value, name))
            else:
                value = g.get_cfg(var)
                action(('%s' % value) if value else 'No global %s set' % (name))
        else:
            # Find the root of the program
            program = Program(os.getcwd())
            if program.is_cwd and not var == 'ROOT':
                error(
                    "Could not find aos program in current path \"%s\".\n"
                    "Change the current directory to a valid aos program, set the current directory as an aos program with 'aos config root .', or use the '--global' option to set global configuration." % program.path)
            with cd(program.path):
                if unset:
                    program.set_cfg(var, None)
                    action('Unset default %s in program "%s"' % (name, program.name))
                elif value:
                    program.set_cfg(var, value)
                    action('%s now set as default %s in program "%s"' % (value, name, program.name))
                else:
                    value = program.get_cfg(var)
                    action(('%s' % value) if value else 'No default %s set in program "%s"' % (name, program.name))
    else:
        subcommands['config'].error("too few arguments")

def _call_scons_target(target, command, aos_path, extra_args=None):
    """ Call scons to run specific command """
    sconscript = os.path.join(aos_path, 'ucube.py')
    if not os.path.exists(sconscript):
        sconscript = os.path.join(aos_path, 'build/ucube.py')

    make_args = ['scons -f ' + sconscript + ' COMMAND=' + command]

    target_find = False

    if '@' in target and not target_find:
        targets = target.split('@')
        if len(targets) < 2:
            error('Must special app and board when build aos')

        app = 'APPLICATION='+targets[0]
        board = 'BOARD=' + targets[1]
        make_args.append(app)
        make_args.append(board)

        if len(targets) == 3:
            build_type = 'TYPE=' + targets[2]
            make_args.append(build_type)

        target_find = True

    if extra_args:
        make_args += extra_args

    ret = popen(' '.join(make_args), shell=True, cwd=os.getcwd())

    return ret

# upload command
@subcommand('upload',
            dict(name='target', help='aos target, e.g. helloworld@starterkit'),
            dict(name=['-w', '--work-path'], dest='work_path',
                 help='Alternative work path if aos_sdk_path is unavailable'),
            dict(name=['-b', '--binaries-dir'], dest='bin_dir',
                 help='Dir to store upload binaries'),
            help='Upload aos image',
            description="Upload aos image to target platform.")

def upload(target, work_path=None, bin_dir=None):
    from .constant import ver
    log('aos-cube version: %s\n' %ver)
    log("[INFO]: Target: %s\n" % target)

    if work_path:
        if os.path.isdir(work_path):
            aos_path = work_path
        else:
            error("Can't find dir %s" % work_path)
    else:
        if os.path.isdir('./kernel/rhino') == False:
            log("[INFO]: Not in aos_sdk_path, curr_path:'%s'\n" % os.getcwd())
            aos_path = Global().get_cfg(AOS_SDK_PATH)
            if aos_path == None:
                error("[ERRO]: Not in aos_sdk_path, aos_sdk unavailable as well. Please run 'aos new $prj_name'!")
            else:
                log("[INFO]: Config Loading OK, use '%s' as sdk path\n" % aos_path)
        else:
            aos_path = os.getcwd()
            log("[INFO]: Currently in aos_sdk_path: '%s'\n" % os.getcwd())

    if '@' not in target or len(target.split('@')) != 2:
        error('Target invalid')
        return;

    extra_args = []
    extra_args += ['WORKPATH=' + aos_path]

    if bin_dir and not os.path.isdir(bin_dir):
        error("Can't find dir %s" % bin_dir)

    extra_args = []
    if work_path:
        extra_args += ['WORKPATH=' + work_path]
    if bin_dir:
        extra_args += ['BINDIR=' + bin_dir]

    _call_scons_target(target, 'upload', aos_path, extra_args)

# debug command
@subcommand('debug',
            dict(name='target', help='aos target, e.g. helloworld@starterkit'),
            dict(name=['-w', '--work-path'], dest='work_path',
                 help='Alternative work path if aos_sdk_path is unavailable'),
            dict(name=['-b', '--binaries-dir'], dest='bin_dir',
                 help='Dir to store debug binaries'),
            dict(name=['-c', '--client'], dest='start_client', action='store_true',
                 help='Start gdb client'),
            dict(name=['-a', '--args'], dest='gdb_args',
                 help='Arguments pass to gdb client'),
            help='Debug aos image',
            description="Initialize debug env for aos image.")

def debug(target, work_path=None, bin_dir=None, start_client=False, gdb_args=None):
    from .constant import ver
    log('aos-cube version: %s\n' %ver)
    log("[INFO]: Target: %s\n" % target)

    if work_path:
        if os.path.isdir(work_path):
            aos_path = work_path
        else:
            error("Can't find dir %s" % work_path)
    else:
        if os.path.isdir('./kernel/rhino') == False:
            log("[INFO]: Not in aos_sdk_path, curr_path:'%s'\n" % os.getcwd())
            aos_path = Global().get_cfg(AOS_SDK_PATH)
            if aos_path == None:
                error("[ERRO]: Not in aos_sdk_path, aos_sdk unavailable as well. Please run 'aos new $prj_name'!")
            else:
                log("[INFO]: Config Loading OK, use '%s' as sdk path\n" % aos_path)
        else:
            aos_path = os.getcwd()
            log("[INFO]: Currently in aos_sdk_path: '%s'\n" % os.getcwd())

    if '@' not in target or len(target.split('@')) != 2:
        error('Target invalid')
        return;

    if work_path and not os.path.isdir(work_path):
        error("Can't find dir %s" % work_path)

    if bin_dir and not os.path.isdir(bin_dir):
        error("Can't find dir %s" % bin_dir)

    extra_args = []
    if work_path and os.path.isdir(work_path):
        extra_args += ['WORKPATH=' + work_path]

    if bin_dir and os.path.isdir(bin_dir):
        extra_args += ['BINDIR=' + bin_dir]

    if start_client:
        extra_args += ['STARTCLIENT=True']

    if gdb_args:
        extra_args += ['GDBARGS="' + gdb_args + '"']

    _call_scons_target(target, 'debug', aos_path, extra_args)

# monitor command
@subcommand('monitor',
            dict(name='port', help='Choose serial port'),
            dict(name='baud', help='Select baudrate'),
            help='Serial port monitor\n\n',
            description="Open a simple serial monitor.")
def monitor(port, baud):
    args = ['miniterm', port, baud]
    host_os = get_host_os()
    if host_os != 'Win32':
        args.append('--eol')
        args.append('LF')
    sys.argv = args
    try:
        miniterm.main()
    except ProcessException as e:
        raise e

@subcommand('devices',
            help='List devices on serial ports\n\n',
            description="List devices on serial ports.")
def devices():
    arr = []
    for p in comports():
        j = json.dumps(p.__dict__)
        arr.append(json.loads(j))
    print(json.dumps(arr, indent = 4))
    sys.exit(0)

@subcommand('upgrade',
            help='Upgrade aos-cube to latest',
            description="Run pip upgrade process to keep aos-cube up-to-date.")
def upgrade():
    cmd = ["pip", "install", "--upgrade", "aos-cube"]
    try:
        ret = popen(cmd)
        if ret != 0:
            cmd.insert(3, "--no-cache-dir")
            popen(cmd)
    except Exception as e:
        raise e

@subcommand('help',
            help='This help screen')
def help_():
    return parser.print_help()


def main():
    global verbose, very_verbose, remainder, cwd_root

    reload(sys)
    sys.setdefaultencoding('UTF8')

    # Help messages adapt based on current dir
    cwd_root = os.getcwd()

    if sys.version_info[0] != 2 or sys.version_info[1] < 7:
        error(
            "aos cube is compatible with Python version >= 2.7 and < 3.0\n"
            "Please refer to the online guide available at https://code.aliyun.com/aos/aos-cube")

    # Parse/run command
    if len(sys.argv) <= 1:
        help_()
        sys.exit(1)

    if '--version' in sys.argv:
        log(ver + "\n")
        sys.exit(0)

    pargs, remainder = parser.parse_known_args()
    status = 1

    try:
        very_verbose = pargs.very_verbose
        verbose = very_verbose or pargs.verbose
        info('Working path \"%s\" (%s)' % (os.getcwd(), Repo.pathtype(cwd_root)))
        status = pargs.command(pargs)
    except ProcessException as e:
        error(
            "\"%s\" returned error code %d.\n"
            "Command \"%s\" in \"%s\"" % (e[1], e[0], e[2], e[3]), e[0])
    except OSError as e:
        traceback.print_exc()
        if e[0] == errno.ENOENT:
            error(
                "Could not detect one of the command-line tools.\n"
                "You could retry the last command with \"-v\" flag for verbose output\n", e[0])
        else:
            error('OS Error: %s' % e[1], e[0])
    except KeyboardInterrupt as e:
        info('User aborted!', -1)
        sys.exit(255)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        if very_verbose:
            traceback.print_exc(file=sys.stdout)
        error("Unknown Error: %s" % e, 255)
    sys.exit(status or 0)


if __name__ == "__main__":
    main()
