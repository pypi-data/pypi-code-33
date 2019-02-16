# -*- coding: utf-8 -*-
"""Backends for 'msbackup' package."""

import os
import shutil
import subprocess
import sys
import tempfile
import abc

try:
    from msbackup import utils, archive, encrypt
except ImportError:  # pragma: no coverage
    import utils
    import archive
    import encrypt


class Base(metaclass=abc.ABCMeta):
    """Base back-end."""

    SECTION = 'DEFAULT'

    def __init__(self, config, archiver=None, encryptor=None, exclude=None,
                 out=None, err=None):
        """
        Constructor.

        :param config: Config object.
        :type config: :class:`ConfigParser.RawConfigParser`
        :param archiver: Name of file archiver.
        :type archiver: basestring
        :param encryptor: Name of file encryptor.
        :type encryptor: basestring
        :param exclude: List of excludes.
        :type exclude: list
        :param out: Output stream.
        :param err: Output stream of error messages.
        """
        self.stream_out = sys.stdout if out is None else out
        self.stream_err = sys.stderr if err is None else err
        # Encryptor
        if encryptor is not None:
            encryptor_name = encryptor
        else:
            encryptor_name = config.get(
                self.SECTION, 'ENCRYPTOR', fallback=None)
        if encryptor_name is not None:
            self.encryptor = encrypt.make_encryptor(encryptor_name, config)
        else:
            self.encryptor = None
        # Archiver
        if archiver is not None:
            archiver_name = archiver
        else:
            archiver_name = config.get(
                self.SECTION,
                'ARCHIVER',
                fallback='tar',
            )
        self.archiver = archive.make_archiver(
            name=archiver_name,
            config=config,
            encryptor=self.encryptor,
        )
        if exclude is None:
            exclude = []
        exclude_conf = config.get(self.SECTION, 'EXCLUDE', fallback=None)
        if exclude_conf is not None:
            exclude_conf = utils.dequote(exclude_conf)
            exclude.extend(exclude_conf.split(','))
        exclude_from = config.get(self.SECTION, 'EXCLUDE_FROM', fallback=None)
        if exclude_from is not None:
            if (not os.path.isabs(exclude_from) and
                    hasattr(config, 'config_file_path')):
                exclude_from = os.path.join(
                    os.path.dirname(getattr(config, 'config_file_path')),
                    exclude_from,
                )
            with open(exclude_from, 'r') as ex_file:
                for line in ex_file.readlines():
                    exclude.append(line.strip())
        self.exclude = exclude if len(exclude) > 0 else None
        # File methods.
        self.open = open
        self.compressor_cmd = None

    def _compress(self, in_stream, out_stream):
        """Сжатие потока in_stream в выходной поток out_stream."""
        return utils.compress(
            *self.compressor_cmd,
            in_stream=in_stream,
            out_stream=out_stream)

    def outpath(self, archive_dir, name):
        """
        Generate archive file name.

        :param archive_dir: Path to archive directory.
        :type archive_dir: basestring
        :param name: Name of archive file without extensions.
        :type name: basestring
        :return: Full path to archive file.
        :rtype: basestring
        """
        fname = name + self.archiver.suffix
        return os.path.join(archive_dir, fname)

    @abc.abstractmethod
    def archive(self, source, output, base_dir=None):
        """
        Archive object.

        :param source: Source identifier.
        :type source: basestring
        :param output: Path to archive file.
        :type output: basestring
        :param base_dir: Path to base directory of source.
        :type base_dir: basestring
        :return: Exit code.
        :rtype: int
        """

    @abc.abstractmethod
    def backup(self, source, archive_dir, verbose=False):
        """
        Backup object.

        :param source: Source identifier.
        :type source: basestring
        :param archive_dir: Path to archive directory.
        :type archive_dir: basestring
        :param verbose: Print verbose messages.
        :type verbose: bool
        """

    def out(self, *args):
        """Output data to standard stream."""
        for data in args:
            self.stream_out.write(data)
        else:
            self.stream_out.write('\n')

    def err(self, *args):
        """Output data to error stream."""
        for data in args:
            self.stream_err.write(data)
        else:
            self.stream_err.write('\n')


class File(Base):
    """File backend."""

    SECTION = 'Backend-File'

    def archive(self, source, output, base_dir=None):
        """
        Archive filesystem object.

        :param source: Path to source file or directory.
        :type source: basestring
        :param output: Path to archive file.
        :type output: basestring
        :param base_dir: Path to base directory of source.
        :type base_dir: basestring
        :return: Exit code.
        :rtype: int
        """
        params = {
            'source': source,
            'output': output,
            'base_dir': base_dir,
        }
        if self.exclude is not None:
            params['exclude'] = self.exclude
        return self.archiver.pack(**params)

    def backup(self, source, archive_dir, verbose=False):
        """
        Backup file or directory in filesystem.

        :param source: Path to source in filesystem.
        :type source: basestring
        :param archive_dir: Path to archive directory.
        :type archive_dir: basestring
        :param base_dir: Path to base directory of source.
        :type base_dir: basestring
        :param verbose: Print verbose messages.
        :type verbose: bool
        """
        name = os.path.basename(source)
        if name == '':
            name = os.uname().nodename
        output = self.outpath(archive_dir, name=name)
        base_dir = None
        if os.path.isfile(source):
            stype = 'file'
            base_dir = os.path.dirname(source)
            source = os.path.basename(source)
        else:
            stype = 'directory'
        if verbose:
            self.out('Backup ', stype, ': ', source)
        ec = self.archive(
            source=source,
            output=output,
            base_dir=base_dir,
        )
        if ec != 0:
            self.err('[ERROR!] Failed archive ', stype, ': ', source)
        return ec


class Subversion(Base):
    """Subversion backend."""

    SECTION = 'Backend-Subversion'

    def __init__(self, config, **kwargs):
        """Constructor."""
        super().__init__(config, **kwargs)
        self.svnadmin_cmd = config.get(
            self.SECTION,
            'SVNADMIN_COMMAND',
            fallback='/usr/bin/svnadmin',
        )
        # compressor
        compressor_cmd = [config.get(
            self.SECTION,
            'COMPRESSOR_COMMAND',
            fallback='/bin/gzip',
        )]
        compressor_params = config.get(
            self.SECTION,
            'COMPRESSOR_PARAMS',
            fallback='-q9',
        ).split(' ')
        for param in compressor_params:
            if param:
                compressor_cmd.append(param)
        self.compressor_cmd = compressor_cmd
        self.compressor_suffix = config.get(
            self.SECTION,
            'COMPRESSOR_SUFFIX',
            fallback='.gz',
        )

    def outpath(self, archive_dir, name):
        """
        Generate archive file name.

        :param archive_dir: Path to archive directory.
        :type archive_dir: basestring
        :param name: Name of archive file without extensions.
        :type name: basestring
        :return: Full path to archive file.
        :rtype: basestring
        """
        fname = name + '.svn' + self.compressor_suffix
        return os.path.join(archive_dir, fname)

    def archive(self, source, output):
        """
        Archive Subversion repository.

        :param source: Path to source repository.
        :type source: basestring
        :param output: Path to archive file.
        :type output: basestring
        :return: Exit code.
        :rtype: int
        """
        name = os.path.basename(source)
        repo_copy_dir = tempfile.mkdtemp()
        repo_copy = os.path.join(repo_copy_dir, name)
        with self.open(os.devnull, 'wb') as out:
            ec = subprocess.call(
                [self.svnadmin_cmd, 'hotcopy', '--clean-logs', source,
                 repo_copy],
                stdout=out,
            )
        if ec != 0:
            return ec
        tmp_path = output + '.tmp'
        p1 = subprocess.Popen(
            [self.svnadmin_cmd, 'dump', '--quiet', '--deltas', repo_copy],
            stdout=subprocess.PIPE,
        )
        with self.open(tmp_path, 'wb') as out:
            ec = self._compress(in_stream=p1.stdout, out_stream=out)
        shutil.rmtree(repo_copy_dir, ignore_errors=True)
        if ec != 0:
            return ec
        if self.encryptor is not None:
            output += self.encryptor.suffix
            ec = self.encryptor.encrypt(tmp_path, output)
            os.remove(tmp_path)
        else:
            shutil.move(tmp_path, output)
        os.chmod(output, self.archiver.ARCHIVE_PERMISSIONS)
        return ec

    def backup(self, source, archive_dir, verbose=False):
        """
        Backup of all Subversion repositories in repos directory.

        :param repos_dir: Path to repos directory.
        :type repos_dir: basestring
        :param archive_dir: Path to archive directory.
        :type archive_dir: basestring
        :param verbose: Print verbose messages.
        :type verbose: bool
        :return: Exit code.
        :rtype: int
        """
        retvalue = 0
        for repo in os.listdir(source):
            if (self.exclude is not None and repo in self.exclude):
                if verbose is True:  # pragma: no coverage
                    self.out('Exclude repo: ', repo)
                continue
            repo_path = os.path.join(source, repo)
            if not os.path.isdir(repo_path):
                continue
            svnfmt = os.path.join(repo_path, 'format')
            if not (os.path.exists(svnfmt) and os.path.isfile(svnfmt)):
                continue
            if verbose is True:
                self.out('Backup repo: ', repo)
            output = self.outpath(archive_dir, repo)
            ec = self.archive(repo_path, output)
            if ec != 0:
                self.err('[ERROR!] Failed archive repo: ', repo)
                if ec > retvalue:
                    retvalue = ec
        return retvalue


class Mercurial(Base):
    """Mercurial backend."""

    SECTION = 'Backend-Mercurial'

    def archive(self, source, output):
        """
        Archive Mercurial repository.

        :param source: Path to source repository.
        :type source: basestring
        :param output: Path to archive file.
        :type output: basestring
        :return: Exit code.
        :rtype: int
        """
        name = os.path.basename(source)
        repo_bak_dir = tempfile.mkdtemp()
        repo_bak = os.path.join(repo_bak_dir, name)
        ec = subprocess.call(
            ['/usr/bin/hg', 'clone', '--noupdate', '--quiet', source,
             repo_bak],
            stdout=self.stream_out,
            stderr=self.stream_err,
        )
        if ec != 0:
            return ec
        ec = self.archiver.pack(name, output, repo_bak_dir)
        shutil.rmtree(repo_bak_dir, ignore_errors=True)
        return ec

    def backup(self, source, archive_dir, verbose=False):
        """
        Backup of all Mercurial repositories in repos directory.

        :param repos_dir: Path to repos directory.
        :type repos_dir: basestring
        :param archive_dir: Path to archive directory.
        :type archive_dir: basestring
        :param verbose: Print verbose messages.
        :type verbose: bool
        :return: Exit code.
        :rtype: int
        """
        retvalue = 0
        for repo in os.listdir(source):
            if self.exclude is not None and repo in self.exclude:
                if verbose:  # pragma: no cover
                    self.out('Exclude repo: ', repo)
                continue
            repo_path = os.path.join(source, repo)
            if not os.path.isdir(repo_path):
                continue
            hgdir = os.path.join(repo_path, '.hg')
            if not (os.path.exists(hgdir) and os.path.isdir(hgdir)):
                continue
            if verbose:
                self.out('Backup repo: ', repo)
            output = self.outpath(archive_dir, os.path.basename(repo_path))
            ec = self.archive(repo_path, output)
            if ec != 0:
                self.err('[ERROR!] Failed archive repo: ', repo)
                if ec > retvalue:
                    retvalue = ec
        return retvalue


class PostgreSQL(Base):
    """PostgreSQL backend."""

    SECTION = 'Backend-PostgreSQL'

    FORMAT_NONE = 0  # Формат архива не задан.
    FORMAT_PLAIN = 1  # Полный архив БД в текстовом формате.
    FORMAT_CUSTOM = 2  # Полный архив БД в сжатом формате.

    FORMAT_MAP = {
        'plain': FORMAT_PLAIN,
        'custom': FORMAT_CUSTOM,
        'default': FORMAT_NONE,
    }

    MODE_NONE = 0  # Запрет архивирования БД.
    MODE_SCHEMA = 1  # Архивировать только схему БД.
    MODE_FULL = 2  # Полный архив БД.

    def __init__(self, config, **kwargs):
        """
        Constructor.

        :param config: Config object.
        :type config: :class:`ConfigParser.RawConfigParser`
        :param out: Output stream.
        :param err: Output stream of error messages.
        :param encryptor: Name of file encryptor.
        :type encryptor: basestring
        """
        super().__init__(config, **kwargs)
        # hostname
        self.hostname = config.get(
            self.SECTION,
            'HOSTNAME',
            fallback=None,
        )
        # port
        self.port = config.get(
            self.SECTION,
            'PORT',
            fallback=None,
        )
        # username
        self.username = config.get(
            self.SECTION,
            'USERNAME',
            fallback=None,
        )
        # format
        format_name = config.get(
            self.SECTION,
            'BACKUP_FORMAT',
            fallback='plain',
        )
        if format_name in self.FORMAT_MAP:
            self.format = self.FORMAT_MAP[format_name]
        else:
            raise Exception('Invalid backup format name: {}'
                            .format(format_name))
        # schema_only_list
        self.schema_only_list = []
        lst = utils.dequote(config.get(
            self.SECTION,
            'SCHEMA_ONLY_LIST',
            fallback=utils.EmptyListString(),
        ))
        self.schema_only_list.extend(lst.split(' '))
        # psql_cmd
        self.psql_cmd = config.get(
            self.SECTION,
            'PSQL_COMMAND',
            fallback='/usr/bin/psql',
        )
        # pgdump_cmd
        self.pgdump_cmd = config.get(
            self.SECTION,
            'PGDUMP_COMMAND',
            fallback='/usr/bin/pg_dump',
        )
        # compressor
        self.compressor_cmd = config.get(
            self.SECTION,
            'COMPRESSOR_COMMAND',
            fallback='/bin/gzip',
        )
        self.compressor_suffix = config.get(
            self.SECTION,
            'COMPRESSOR_SUFFIX',
            fallback='.gz',
        )
        self.compressor_params = config.get(
            self.SECTION,
            'COMPRESSOR_PARAMS',
            fallback='-q9',
        ).split(' ')

    def outpath(self, archive_dir, name, mode=MODE_NONE):
        """
        Generate archive file name.

        :param archive_dir: Path to archive directory.
        :type archive_dir: basestring
        :param name: Name of archive file without extensions.
        :type name: basestring
        :return: Full path to archive file.
        :rtype: basestring
        """
        fname = name
        if mode == self.MODE_SCHEMA:
            fname += '_SCHEMA.sql'
            fname += self.compressor_suffix
        elif self.format == self.FORMAT_PLAIN:
            fname += '.sql'
            fname += self.compressor_suffix
        elif self.format == self.FORMAT_CUSTOM:
            fname += '.custom'
        else:
            fname += self.compressor_suffix
        return os.path.join(archive_dir, fname)

    def archive(self, source, output, mode=MODE_NONE):
        """
        Archive PostgreSQL database.

        :param source: Database name.
        :type source: basestring
        :param output: Path to archive file.
        :type output: basestring
        :param mode: Archive mode.
        :type mode: int
        :return: Exit code.
        :rtype: int
        """
        tmp_path = output + self.archiver.progress_suffix
        if self.format == self.FORMAT_CUSTOM:
            ec = self.dump_proc(
                database=source,
                output=tmp_path,
                mode=mode,
            ).wait()
        else:
            p1 = self.dump_proc(
                database=source,
                output=tmp_path,
                mode=mode,
                stdout=subprocess.PIPE,
            )
            with self.open(tmp_path, 'wb') as out:
                proc = subprocess.Popen(
                    ['/bin/gzip', '-q9'],
                    stdin=p1.stdout,
                    stdout=out,
                )
            p1.stdout.close()
            ec = proc.wait()
        if ec != 0:
            return ec
        if self.encryptor is not None:
            output += self.encryptor.suffix
            ec = self.encryptor.encrypt(source=tmp_path, output=output)
            os.remove(tmp_path)
        else:
            shutil.move(tmp_path, output)
        return ec

    def backup(self, source, archive_dir, verbose=False):
        """
        Backup PostgreSQL databases.

        :param source: Database server host or socket directory.
        :type source: basestring
        :param archive_dir: Path to archive directory.
        :type archive_dir: basestring
        :param base_dir: Path to base directory of source (ignored).
        :type base_dir: basestring
        :param verbose: Print verbose messages.
        :type verbose: bool
        """
        retvalue = 0
        dblist = [source] if source is not None else self.dblist()
        for database in dblist:
            if self.exclude is not None and database in self.exclude:
                if verbose is True:  # pragma: no cover
                    self.out('Exclude database: ', database)
                continue
            mode = (self.MODE_SCHEMA if database in self.schema_only_list
                    else self.MODE_FULL)
            if verbose is True:
                info = ''
                if mode == self.MODE_SCHEMA:
                    info = 'Schema-only'
                elif self.format == self.FORMAT_PLAIN:
                    info = 'Plain'
                elif self.format == self.FORMAT_CUSTOM:
                    info = 'Custom'
                else:
                    info = 'Default'
                self.out(info, ' backup database: ', database)
            ec = self.archive(
                source=database,
                output=self.outpath(archive_dir, database, mode),
                mode=mode,
            )
            if ec != 0:
                if ec > retvalue:
                    retvalue = ec
                self.err('[ERROR!] Failed backup database: ', database)
        return retvalue

    def dblist(self):
        """
        Database list on the target host.

        :return: List of all databases.
        :rtype: list
        """
        params = [self.psql_cmd]
        if self.hostname:
            params.append('--host={}'.format(self.hostname))
        if self.port:
            params.append('--port={}'.format(self.port))
        if self.username:
            params.append('--username={}'.format(self.username))
        params.append('--no-password')
        params.append('--no-align')
        params.append('--tuples-only')
        params.append('-c')
        params.append('SELECT datname '
                      'FROM pg_database '
                      'WHERE NOT datistemplate '
                      'ORDER BY datname;')
        params.append('postgres')
        out = subprocess.check_output(params)
        return out.decode(sys.getdefaultencoding()).splitlines()

    def dump_proc(self, database, output, mode, **kwargs):
        """
        Create process of dump PostgreSQL database.

        :param database: Database name.
        :type database: basestring
        :param output: Path to archive file.
        :type output: basestring
        :param mode: Database backup mode.
        :type mode: int
        :param **kwargs: Arguments of `subprocess.Popen()` constructor.
        :type **kwargs: dict
        """
        params = [self.pgdump_cmd]
        if mode == self.MODE_SCHEMA or self.format == self.FORMAT_PLAIN:
            params.append('--format=p')
        elif self.format == self.FORMAT_CUSTOM:
            params.append('--format=c')
        if mode == self.MODE_SCHEMA:
            params.append('--schema-only')
        if self.hostname:
            params.append('--host={}'.format(self.hostname))
        if self.port:
            params.append('--port={}'.format(self.port))
        if self.username:
            params.append('--username={}'.format(self.username))
        params.append('--no-password')
        params.append('--oids')
        if self.format == self.FORMAT_CUSTOM:
            params.append('--file={}'.format(output))
        params.append(database)
        return subprocess.Popen(params, **kwargs)


BACKENDS = {
    'file': File,
    'subversion': Subversion,
    'mercurial': Mercurial,
    'postgresql': PostgreSQL,
}


def make_backend(name, config, archiver=None, encryptor=None, exclude=None,
                 out=None, err=None):
    """
    Create back-end object.

    :param name: Name of back-end to create.
    :type name: basestring
    :param config: Config object.
    :type config: :class:`ConfigParser.RawConfigParser`
    :param archiver: Name of file archiver.
    :type encryptor: basestring
    :param encryptor: Name of file encryptor.
    :type encryptor: basestring
    :param out: Output stream.
    :param err: Output stream of error messages.
    """
    if name not in BACKENDS:
        raise Exception('Unknown back-end: {}'.format(name))
    return BACKENDS[name](
        config=config,
        archiver=archiver,
        encryptor=encryptor,
        exclude=exclude,
        out=out,
        err=err,
    )
