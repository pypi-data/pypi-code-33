#! /usr/local/bin/python3
# encoding: utf-8
# Author: LiTing

import os
import sys
import getopt
from enum import Enum, unique
import subprocess

# add search path
sys.path.append(os.path.abspath(os.path.curdir))
from .utils import *


def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'm:i:n:o:', ['buildmode', 'inputpath', 'productname', 'outputpath'])
    except getopt.GetoptError:
        print('xxx.py [-m <debug/release>] -i <path> -n <name> -o <path>')
        sys.exit(2)

    global buildmode, inputpath, outputpath, productname

    for opt, arg in opts:
        if opt in ['-m', '--buildmode']:
            buildmode = BuildMode.debug.value if arg.lower() == BuildMode.debug.value else BuildMode.release.value
        if opt in ['-i', '--inputpath']:
            inputpath = arg
        elif opt in ['-n', '--productname']:
            productname = arg
        elif opt in ['-o', '--outputpath']:
            outputpath = arg

    __do_exec()


@unique
class BuildMode(Enum):
    release = 'release'
    debug = 'debug'
    # test = 'debug'

buildmode = BuildMode.debug.value
inputpath = ''
outputpath = ''
productname = ''


def __do_exec():
    PrintWithColor.black('')
    if len(productname) <= 0:
        PrintWithColor.red(f'product name is not a valid name: {productname}')
        return
    if not os.path.isdir(inputpath):
        PrintWithColor.red(f'input path is not a valid dir: {inputpath}')
        return
    if not os.path.isdir(outputpath):
        PrintWithColor.red(f'output path is not a valid dir: {outputpath}')
        return

    # find macho and linkmap
    src_macho_path = ''
    src_linkmap_path = ''

    # lower folder name
    exclude_folders = {f'{productname}.app.dsym'}
    exclude_buildmode = BuildMode.debug.value if buildmode == BuildMode.release.value else BuildMode.release.value
    exclude_folders |= {f'{buildmode}-{x}' for x in {'iphonesimulator', 'watchos', 'watchsimulator'}}
    exclude_folders |= {f'{exclude_buildmode}-{x}' for x in {'iphoneos', 'iphonesimulator', 'watchos', 'watchsimulator'}}
    for root, dirs, files in os.walk(inputpath):
        mdirs = dirs.copy()
        for name in mdirs:
            if name.lower() in exclude_folders:
                dirs.remove(name)
        for file in files:
            if file == f'{productname}':
                src_macho_path = os.path.join(root, file)
                PrintWithColor.yellow(f'find MachO file: {src_macho_path}')
            elif file == f'{productname}-LinkMap-normal-arm64.txt':
                src_linkmap_path = os.path.join(root, file)
                PrintWithColor.yellow(f'find Linkmap file: {src_linkmap_path}')

    if not os.path.isfile(src_macho_path):
        PrintWithColor.red(f'MachO file not found.')
        return
    if not os.path.isfile(src_linkmap_path):
        PrintWithColor.red(f'Linkmap file not found.')
        return

    # dest dir
    dest_dir1 = os.path.join(outputpath, '物料')
    if not os.path.exists(dest_dir1):
        os.makedirs(dest_dir1)
    dest_dir2 = os.path.join(outputpath, 'otool')
    if not os.path.exists(dest_dir2):
        os.makedirs(dest_dir2)

    if not os.path.isdir(dest_dir1):
        PrintWithColor.red(f'not a valid dir: {dest_dir1}')
        return
    if not os.path.isdir(dest_dir2):
        PrintWithColor.red(f'not a valid dir: {dest_dir2}')
        return

    # dest file path
    dest_macho_path = os.path.join(dest_dir1, productname)
    dest_linkmap_path = os.path.join(dest_dir1, f'{productname}-LinkMap-normal-arm64.txt')
    dest_classlist_path = os.path.join(dest_dir2, 'objc_classlist.txt')
    dest_classrefs_path = os.path.join(dest_dir2, 'objc_classrefs.txt')

    # copy macho and linkmap
    PrintWithColor.yellow(f'copying macho to: {dest_macho_path}')
    os.system(f'cp {src_macho_path} {dest_macho_path}')
    # os.system(f'cp {src_linkmap_path} {dest_linkmap_path}')

    # 不要直接copy，因为源文件编码格式不是utf-8，所以这里先转一下编码再保存，解放劳动力，避免手动用sublime转码（网上资料都是手动转）
    # 经过不断的尝试，终于发现`iconv -l | grep -i mac`这个命令列出的MAC编码是可以decode原始linkmap文件的。ASCII GB18030
    PrintWithColor.yellow(f'encoding utf8 linkmap to: {dest_linkmap_path}')
    src_linkmap_encoding = 'MAC'
    os.system(f'iconv -f {src_linkmap_encoding} -t UTF-8 {src_linkmap_path} | cat > {dest_linkmap_path}')

    # otool -> sections
    PrintWithColor.yellow(f'extracting _objc_classlist to: {dest_classlist_path}')
    objc_classlist_bytes = subprocess.check_output(f'otool -arch arm64 -s __DATA __objc_classlist {dest_macho_path}', shell=True)
    objc_classlist_output = str(objc_classlist_bytes, encoding='utf-8')
    # os.system(f'echo {objc_classlist_output} > {dest_classlist_path}')
    with open(dest_classlist_path, 'w+', encoding='utf-8') as fo:
        fo.write(objc_classlist_output)

    PrintWithColor.yellow(f'extracting _objc_classrefs to: {dest_classrefs_path}')
    objc_classrefs_bytes = subprocess.check_output(f'otool -arch arm64 -s __DATA __objc_classrefs {dest_macho_path}', shell=True)
    objc_classrefs_output = str(objc_classrefs_bytes, encoding='utf-8')
    # os.system(f'echo {objc_classrefs_output} > {dest_classrefs_path}')
    with open(dest_classrefs_path, 'w+', encoding='utf-8') as fo:
        fo.write(objc_classrefs_output)

    PrintWithColor.blue('--- end ---')


if __name__ == '__main__':
    main(sys.argv[1:])


# TEST
# if __name__ == '__main__':
#     main([
#         '-m', 'debug',
#         '-i', '/Users/match/Library/Developer/Xcode/DerivedData/test-linkmap-sections-cnwmefvqitnbhxdljpyocdcuumcf',
#         '-n', 'test-linkmap-sections',
#         '-o', '/Users/match/Desktop/包大小/linkmap/项目/test-linkmap-sections'
#     ])

    # main(['-m', 'release',
    #       '-i', '/Users/match/Library/Developer/Xcode/DerivedData/newxiami-dkmguzzouxemxadrxgcoauukbzbq',
    #       '-n', 'xiami',
    #       '-o', '/Users/match/Desktop/包大小/linkmap/项目/xiami'])
