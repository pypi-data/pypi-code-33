# -*- coding: utf-8 -*-
import io
import logging
import sys

import mysql.connector


class DatabaseTools:
    def __init__(self, logger=None):
        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger

    def connect_database(self, db_params):
        try:
            host, user, password, name = db_params
            self.logger.debug(
                "Connecting to database with details: "
                "user={user}, password={password}, host={host}, db={db}".format
                (user=user, password=password, host=host, db=name)
            )

            db_connection = mysql.connector.connect(user=user,
                                                    password=password,
                                                    host=host,
                                                    database=name)
            db_connection.autocommit = True
            return db_connection

        except mysql.connector.Error as error:
            self.logger.error(
                "{} while connecting to database: {}".format(
                    type(error).__name__,
                    error))
            sys.exit(1)

    def fetch_current_version(self, db_params):
        current_db_version = 0
        try:
            db_connection = self.connect_database(db_params)
            cursor = db_connection.cursor()
            cursor.execute("SELECT version FROM versionTable LIMIT 1")
            current_db_version = int(cursor.fetchone()[0])
            db_connection.close()
        except mysql.connector.Error as error:
            self.logger.error(
                "{} while attempting to fetch database version, assuming"
                " version 0: {}".format(type(error).__name__, error)
            )
        return current_db_version

    def apply_migration(self, db_params, sql_filename):
        with io.open(sql_filename) as sql_file:
            db_connection = self.connect_database(db_params)
            cursor = db_connection.cursor()
            cursor.execute(sql_file.read(), multi=True)
            db_connection.close()
