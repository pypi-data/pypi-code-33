# -*- coding: utf-8 -*-
import logging

import mysql.connector

from migration_runner.database_tools import DatabaseTools
from migration_runner.helpers import Helpers


class Controller:
    def __init__(self, logger=None):
        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger

        self.helpers = Helpers(logger)
        self.database = DatabaseTools(logger)

    def process_single_file(self, db_params, single_file):
        self.logger.warning(
            "Use of this option means DB version will be out of sync!")

        self.database.apply_migration(db_params, single_file)

        self.logger.info(
            "Successfully executed SQL in file: '{}'".format(single_file)
        )

    def update_current_version(self, db_params, new_version):
        current_db_version = 0
        try:
            db_connection = self.database.connect_database(db_params)
            cursor = db_connection.cursor()
            cursor.execute("UPDATE versionTable SET version = \'{}\'"
                           .format(new_version))
            cursor.execute("SELECT version FROM versionTable LIMIT 1")
            db_version_row = cursor.fetchone()
            if db_version_row is not None:
                current_db_version = db_version_row[0]
            db_connection.close()
        except mysql.connector.Error as error:
            self.logger.error(
                "{} while attempting to update current database version, "
                "assuming version 0: {}".format(type(error).__name__, error)
            )
        return current_db_version

    def process_migrations(self, db_params, db_version,
                           unprocessed_migrations):
        total_processed = 0
        for version_code, sql_filename in unprocessed_migrations:
            self.logger.debug(
                "Applying migration: {version} with filename: '{file}'".format
                (version=version_code, file=sql_filename)
            )
            try:
                self.database.apply_migration(db_params, sql_filename)
                self.logger.info(
                    "Successfully upgraded database from version: {old} to"
                    " {new} by executing migration in file: '{file}'".format(
                        old=db_version, new=version_code, file=sql_filename)
                )

                db_version = self.update_current_version(db_params,
                                                         version_code)
                total_processed += 1
            except mysql.connector.Error as error:
                self.logger.error(
                    "{type} while processing migration in file: '{file}': "
                    "{error}".format(type=type(error).__name__,
                                     file=sql_filename,
                                     error=error))
                break
        return db_version, total_processed

    def process_migrations_in_directory(self, db_params, sql_directory):
        self.logger.debug(
            "Looking for migrations in dir: {}".format(sql_directory))

        migrations = self.helpers.populate_migrations(sql_directory)
        self.logger.debug("Migrations found: {}".format(len(migrations)))

        db_version = self.database.fetch_current_version(db_params)
        self.logger.info(
            "Starting with database version: {}".format(db_version))

        unprocessed = self.helpers.get_unprocessed_migrations(db_version,
                                                              migrations)
        self.logger.info(
            "Migrations yet to be processed: {unprocessed} (out of {total} "
            "in dir)".format(
                unprocessed=len(unprocessed),
                total=len(migrations)
            )
        )

        db_version, total_processed = self.process_migrations(
            db_params,
            db_version,
            unprocessed
        )

        self.logger.info(
            "Database version now {version} after processing {processed}"
            " migrations. Remaining: {unprocessed}.".format
            (version=db_version, processed=total_processed,
             unprocessed=(len(unprocessed) - total_processed)))
