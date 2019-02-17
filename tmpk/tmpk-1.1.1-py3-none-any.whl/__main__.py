# Copyright 2018 leoetlino <leo@leolam.fr>
# Licensed under GPLv2+
import argparse
import io
import os
from pathlib import Path
import shutil
import struct
import sys
import typing

from . import tmpk

def tmpk_extract(args) -> None:
    archive_path = Path(args.tmpk)
    with archive_path.open('rb') as f:
        archive = tmpk.Tmpk(f.read())
        result_dir = Path(archive_path.parent / archive_path.stem)
        result_dir.mkdir()
        for name, file in archive.get_files().items():
            target_path = result_dir / Path(name)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with target_path.open('wb') as target_file:
                target_file.write(file.data)
            print(target_path)

def tmpk_list(args) -> None:
    archive_path = args.tmpk
    with open(args.tmpk, 'rb') as f:
        archive = tmpk.Tmpk(f.read())
        for name, file in archive.get_files().items():
            extra_info = "[0x%x bytes]" % len(file.data)
            extra_info += " @ 0x%x" % file.offset
            print("%s%s" % (name, ' ' + extra_info if not args.name_only else ''))

def _write_tmpk(writer: tmpk.TmpkWriter, dest_stream: typing.BinaryIO) -> None:
    buf = io.BytesIO()
    alignment: int = writer.write(buf)
    buf.seek(0)
    shutil.copyfileobj(buf, dest_stream)

def tmpk_create_or_update(args, update: bool) -> None:
    file_list: typing.List[str] = args.files
    dest_file: str = args.dest
    base_path: typing.Optional[str] = args.base_path

    if '!!' in dest_file:
        if len(file_list) != 1:
            sys.stderr.write('error: cannot detect what the output archive name should be from file list\n')
            sys.exit(1)
        dest_file = dest_file.replace('!!', os.path.normpath(file_list[0]))

    if not args.base_path:
        if len(file_list) != 1:
            sys.stderr.write('error: cannot auto detect base path from file list\n')
            sys.exit(1)
        if not os.path.isdir(file_list[0]):
            sys.stderr.write(f'error: {file_list[0]} is not a directory. Did you mix up the argument order? (directory that should be archived first, then the target archive)\n')
            sys.exit(1)
        base_path = file_list[0]

    writer: typing.Optional[tmpk.TmpkWriter] = None
    if not update:
        writer = tmpk.TmpkWriter()
    else:
        with open(dest_file, 'rb') as original_tmpk_file:
            writer = tmpk.make_writer_from_tmpk(tmpk.Tmpk(original_tmpk_file.read()))

    if not writer:
        sys.stderr.write('error: could not create writer (is the original archive valid?)\n')
        sys.exit(1)

    if args.default_alignment:
        writer.set_default_alignment(args.default_alignment)

    dest_stream: typing.BinaryIO = open(dest_file, 'wb') if dest_file != '-' else sys.stdout.buffer

    def add_file(writer, path: str) -> None:
        with open(path, 'rb') as f:
            archive_path = path if not base_path else os.path.relpath(path=path, start=base_path)
            archive_path = archive_path.replace('\\', '/')
            if args.with_leading_slash and archive_path[0] != '/':
                archive_path = '/' + archive_path
            writer.add_file(archive_path, f.read())
            sys.stderr.write(archive_path + '\n')

    for file in file_list:
        if os.path.isfile(file):
            add_file(writer, file)
        else:
            for root, dirs, files in os.walk(file, topdown=False):
                for file_name in files:
                    add_file(writer, os.path.join(root, file_name))

    _write_tmpk(writer, dest_stream)

def tmpk_test_repack(args) -> None:
    archive = tmpk.Tmpk(args.archive.read())
    writer = tmpk.make_writer_from_tmpk(archive)

    original_offsets = archive.get_file_offsets()
    repacked_offsets = writer.get_file_offsets()

    for original_offset, repacked_offset in zip(original_offsets, repacked_offsets):
        if original_offset == repacked_offset:
            print('%s @ 0x%x' % (original_offset[0], original_offset[1]))
        else:
            print('')
            print('!!! mismatch: original: %s @ 0x%x' % (original_offset[0], original_offset[1]))
            print('!!! mismatch: repacked: %s @ 0x%x' % (repacked_offset[0], repacked_offset[1]))
            if original_offset[1] > repacked_offset[1]:
                alignment = 2
                aligned_offset = repacked_offset[1]
                while aligned_offset != original_offset[1]:
                    alignment <<= 1
                    aligned_offset = (aligned_offset + alignment - 1) & -alignment
                print('!!! mismatch: alignment value seems to be 0x%x' % alignment)
            sys.exit(12)

    buf = io.BytesIO()
    writer.write(buf)
    if archive._data != buf.getbuffer():
        print('!!! mismatch: repacked archive is different')
        sys.exit(13)

    print('ok')

def main() -> None:
    parser = argparse.ArgumentParser(description='Tool to manipulate TMPK archives.')

    subparsers = parser.add_subparsers(dest='command', help='Command')
    subparsers.required = True

    x_parser = subparsers.add_parser('extract', description='Extract an archive', aliases=['x'])
    x_parser.add_argument('tmpk', help='Path to a TMPK archive')
    x_parser.set_defaults(func=tmpk_extract)

    l_parser = subparsers.add_parser('list', description='List files in an archive', aliases=['l'])
    l_parser.add_argument('tmpk', help='Path to a TMPK archive')
    l_parser.add_argument('--name-only', action='store_true', help='Show only file names')
    l_parser.set_defaults(func=tmpk_list)

    c_parser = subparsers.add_parser('create', description='Create an archive', aliases=['c'])
    c_parser.add_argument('--base-path', help='Base path to remove from contained file names.')
    c_parser.add_argument('--with-leading-slash', action='store_true', help='Add a leading slash to all paths. Required for some game data archives.')
    c_parser.add_argument('-n', '--default-alignment', type=lambda n: int(n, 0),
                          help='Set the default alignment for files. Defaults to 4.')
    c_parser.add_argument('files', nargs='+', help='Files or directories to include in the archive')
    c_parser.add_argument('dest', help='Destination archive')
    c_parser.set_defaults(func=lambda a: tmpk_create_or_update(a, update=False))

    u_parser = subparsers.add_parser('update', description='Update an archive', aliases=['u'])
    u_parser.add_argument('--base-path', help='Base path to remove from contained file names.')
    u_parser.add_argument('--with-leading-slash', action='store_true', help='Add a leading slash to all paths. Required for some game data archives.')
    u_parser.add_argument('-n', '--default-alignment', type=lambda n: int(n, 0),
                          help='Set the default alignment for files. Defaults to 4.')
    u_parser.add_argument('files', nargs='+', help='Files or directories to add to the archive')
    u_parser.add_argument('dest', help='Archive to update')
    u_parser.set_defaults(func=lambda a: tmpk_create_or_update(a, update=True))

    t_parser = subparsers.add_parser('test-repack', description='Test repacking to check for potential alignment issues')
    t_parser.add_argument('archive', type=argparse.FileType('rb'), help='Archive to test')
    t_parser.set_defaults(func=tmpk_test_repack)

    args = parser.parse_args()
    args.func(args)
