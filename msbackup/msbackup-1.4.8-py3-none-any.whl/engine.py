# -*- coding: utf-8 -*-
"""Backup engine class definition module."""

import calendar
import datetime as mydt
import datetime
from datetime import timedelta
import os
import stat
import re
import shutil
import getpass

from dateutil.relativedelta import relativedelta

try:
    from msbackup import backend as backend_mod
except ImportError:  # pragma: no coverage
    import backend as backend_mod


class Engine(object):
    """Backup engine class."""

    DATE_FORMAT = '%Y-%m-%d'
    COMMON = r'^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})'
    DEFAULT_OPTIONS = {
        'month_suffix': '-monthly',
        'week_suffix': '-weekly',
        'day_suffix': '-daily',
    }
    ARCHIVE_PERMISSIONS = (
        stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP |
        stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
    )

    def __init__(self, backend, config, archiver=None, encryptor=None,
                 exclude=None, out=None, err=None, **kwargs):
        """
        Backup engine constructor.

        :param backend: Backend identifier.
        :param backend: str
        :param config: Config object.
        :type config: :class:`ConfigParser.RawConfigParser`
        :param archiver: Name of file archiver.
        :type archiver: basestring
        :param encryptor: Name of file encryptor.
        :type encryptor: basestring
        :param exclude: List of excludes.
        :type exclude: list
        :param out: Stream to messages output.
        :param err: Stream to errors output.
        """
        if backend not in backend_mod.BACKENDS:
            raise Exception('Unknown back-end: {}'.format(backend))
        # -- Load configuration --
        section = backend_mod.BACKENDS[backend].SECTION
        # backup_user
        backup_user = config.get(section, 'BACKUP_USER', fallback=None)
        if backup_user is not None:
            if getpass.getuser() != backup_user:
                raise Exception('This program must be run as {}. '
                                'Exiting.'.format(backup_user))
        self.source = config.get(section, 'SOURCE', fallback=None)
        self.backup_dir = config.get(section, 'BACKUP_DIR', fallback=None)
        self.day_month_keep = config.getint(
            section, 'DAY_OF_MONTH_TO_KEEP', fallback=1)
        self.months_keep = config.getint(section, 'MONTHS_TO_KEEP', fallback=1)
        self.day_week_keep = config.getint(
            section, 'DAY_OF_WEEK_TO_KEEP', fallback=1)
        self.weeks_keep = config.getint(section, 'WEEKS_TO_KEEP', fallback=4)
        self.days_keep = config.getint(section, 'DAYS_TO_KEEP', fallback=7)
        # -- Options
        options = self.DEFAULT_OPTIONS.copy()
        if kwargs:
            options.update(kwargs)
        self.month_suffix = options['month_suffix']
        self.week_suffix = options['week_suffix']
        self.day_suffix = options['day_suffix']
        self.re_month = re.compile(self.COMMON + self.month_suffix)
        self.re_week = re.compile(self.COMMON + self.week_suffix)
        self.re_day = re.compile(self.COMMON + self.day_suffix)
        # -- Backend
        self.backend = backend_mod.make_backend(
            name=backend,
            config=config,
            archiver=archiver,
            encryptor=encryptor,
            exclude=exclude,
            out=out,
            err=err,
        )

    def out(self, *args):
        """Output data to standard stream."""
        self.backend.out(*args)

    def err(self, *args):
        """Output data to error stream."""
        self.backend.err(*args)

    def backup(self, source=None, backup_dir=None, verbose=False):
        """
        Perform backup of source into archive directory.

        :param source: Path to source of backup.
        :type source: basestring
        :param backup_dir: Path to directory for store archives.
        :type backup_dir: basestring
        :param verbose: Print verbose messages.
        :type verbose: bool
        :return: Path to archive directory.
        :rtype: basestring
        """
        if verbose:
            self.out('Backup started.\n', '----------------------')
        if source is None:
            source = self.source
        if backup_dir is None:
            backup_dir = self.backup_dir
        if not os.path.exists(backup_dir):
            if verbose:
                self.out('Making archive directory in ', backup_dir)
            try:
                os.makedirs(backup_dir, mode=self.ARCHIVE_PERMISSIONS)
            except Exception as ex:
                self.err(
                    'Error creating archive directory "',
                    backup_dir, '": ', str(ex))
                raise
        if verbose:
            self.out('\nPerforming backups\n', '----------------------')
        ec = self.backend.backup(
            source=source,
            archive_dir=backup_dir,
            verbose=verbose,
        )
        if verbose:
            self.out('----------------------\n', 'All backups complete!')
        if ec != 0:
            self.err('Errors occurred, exit code: ', str(ec))
        return backup_dir

    def _remove_expired(self, backup_dir, expire, regexp):
        """
        Remove expired archives based on configuration.

        :param backup_dir: Path to archives directory.
        :type backup_dir: basestring
        :param expire: Datetime of oldest archive to keep.
        :type expire: datetime
        :param regexp: Regular expression to match archive directory.
        :type regexp: regexp
        """
        if not os.path.exists(backup_dir) or not os.path.isdir(backup_dir):
            return
        for entry in os.listdir(backup_dir):
            arch_path = os.path.join(backup_dir, entry)
            if not os.path.isdir(arch_path):
                continue
            m = regexp.match(entry)
            if m:
                entry_date = mydt.date(
                    int(m.group('year')),
                    int(m.group('month')),
                    int(m.group('day')),
                )
                if entry_date <= expire:
                    shutil.rmtree(arch_path, ignore_errors=True)

    def rotated(self, source=None, backup_dir=None, verbose=False):
        """
        Perform rotated archive with removing expired archives.

        :param source: Path to source directory.
        :type source: basestring
        :param backup_dir: Path to archives directory.
        :type backup_dir: basestring
        :param verbose: Print verbosity messages.
        :type verbose: bool
        :return: Path to archive directory.
        :rtype: basestring
        """
        if source is None:
            source = self.source
        if backup_dir is None:
            backup_dir = self.backup_dir
        today = mydt.date.today()
        archive_base_name = today.strftime(self.DATE_FORMAT)
        # Monthly backup.
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        day_month_keep = min(self.day_month_keep, days_in_month)
        if today.day == day_month_keep:
            # Delete expired monthly backups.
            td = datetime.date(today.year, today.month, today.day)
            expire = relativedelta(months=-self.months_keep).__add__(td)
            self._remove_expired(
                backup_dir=backup_dir,
                expire=expire,
                regexp=self.re_month,
            )
            archive_name = archive_base_name + self.month_suffix
            return self.backup(
                source=source,
                backup_dir=os.path.join(backup_dir, archive_name),
                verbose=verbose,
            )
        # Weekly backup.
        if today.isoweekday() == self.day_week_keep:
            expire = today - timedelta(weeks=self.weeks_keep)
            self._remove_expired(
                backup_dir=backup_dir,
                expire=expire,
                regexp=self.re_week,
            )
            archive_name = archive_base_name + self.week_suffix
            return self.backup(
                source=source,
                backup_dir=os.path.join(backup_dir, archive_name),
                verbose=verbose,
            )
        # Daily backup.
        expire = today - timedelta(days=self.days_keep)
        self._remove_expired(
            backup_dir=backup_dir,
            expire=expire,
            regexp=self.re_day,
        )
        archive_name = archive_base_name + self.day_suffix
        return self.backup(
            source=source,
            backup_dir=os.path.join(backup_dir, archive_name),
            verbose=verbose,
        )
