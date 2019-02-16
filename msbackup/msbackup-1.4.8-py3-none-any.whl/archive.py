# -*- coding: utf-8 -*-
"""Archivers module."""

import os
import shutil
import stat
import subprocess


class Tar(object):
    """Tar archiver class."""

    SECTION = 'Archive-Tar'
    ARCHIVE_PERMISSIONS = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP

    def __init__(self, config, encryptor=None):
        """
        Class constructor.

        :param config: Config object.
        :type config: :class:`ConfigParser.RawConfigParser`
        """
        self.cmd = config.get(self.SECTION, 'COMMAND', fallback='/bin/tar')
        self.params = config.get(
            self.SECTION,
            'ARCHIVER_PARAMS',
            fallback='--gzip',
        ).split(' ')
        self.suffix = config.get(self.SECTION, 'SUFFIX', fallback='.tar.gz')
        self.progress_suffix = config.get(
            self.SECTION,
            'PROGRESS_SUFFIX',
            fallback='.in_progress',
        )
        self.encryptor = encryptor
        self.open = open

    def pack(self, source, output=None, base_dir=None, **kwargs):
        """
        Pack files into archive.

        :param source: Path to file to pack.
        :type source: basestring
        :param output: Path to output packed files archive.
        :type output: basestring
        :param base_dir: Path to base archive directory.
        :type base_dir: basestring
        :param extra: Extra tar parameters.
        :type extra: [basestring]
        """
        if output is None:
            if base_dir is None:
                output = source + self.suffix
            else:
                output = os.path.join(base_dir, source + self.suffix)
        tmp_path = output + self.progress_suffix
        params = ['/bin/tar', '--create', '--file', tmp_path]
        params.extend(self.params)
        if base_dir is not None:
            params.extend(['-C', base_dir])
        if 'exclude' in kwargs:
            for ex in kwargs['exclude']:
                params.append('--exclude={}'.format(ex))
        params.append(source)
        with self.open(os.devnull, 'w') as out:
            ec = subprocess.call(params, stdout=out, stderr=subprocess.STDOUT)
        if ec != 0:
            return ec
        if self.encryptor is not None:
            output += self.encryptor.suffix
            ec = self.encryptor.encrypt(tmp_path, output)
            os.remove(tmp_path)
        else:
            shutil.move(tmp_path, output)
        if ec == 0:
            os.chmod(output, self.ARCHIVE_PERMISSIONS)
        return ec


ARCHIVERS = {'tar': Tar}


def make_archiver(name, config, encryptor=None):
    """
    Create archiver object.

    :param name: Name of archiver.
    :type name: basestring
    :param config: Config object.
    :type config: :class:`ConfigParser.RawConfigParser`
    :param encryptor: File encryptor object.
    """
    if name not in ARCHIVERS:
        raise Exception('Unknown archiver: {}'.format(name))
    return ARCHIVERS[name](config, encryptor)
