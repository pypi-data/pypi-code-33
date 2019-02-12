# -*- coding: utf-8 -*-
import logging
import os
import re
import sys


class Helpers:
    def __init__(self, logger=None):
        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger

    @staticmethod
    def extract_sequence_num(filename):
        sequence_num = re.search(
            '([0-9]+)[^0-9].+',
            os.path.basename(filename)
        ).group(1)

        return int(sequence_num)

    def append_migration(self, migrations, filename):
        try:
            migrations.append((self.extract_sequence_num(filename), filename))
        except AttributeError:
            self.logger.error("Invalid filename found: {}".format(filename))
            sys.exit(1)

    def find_migrations(self, sql_directory):
        migrations = []
        for filename in os.listdir(sql_directory):
            if filename.endswith(".sql"):
                self.append_migration(
                    migrations,
                    str(os.path.join(sql_directory, filename))
                )
        return migrations

    @staticmethod
    def sort_migrations(migrations):
        if (
            all(isinstance(tup, tuple) for tup in migrations) and
            all(isinstance(tup[0], int) for tup in migrations) and
            all(isinstance(tup[1], str) for tup in migrations)
        ):
            migrations.sort(key=lambda tup: tup[0])
        else:
            raise TypeError(
                "Migrations list did not contain only tuple(int, str)")

    def populate_migrations(self, sql_directory):
        migrations = self.find_migrations(sql_directory)
        self.sort_migrations(migrations)
        return migrations

    @staticmethod
    def get_unprocessed_migrations(db_version, migrations):
        return [tup for tup in migrations if tup[0] > int(db_version)]
