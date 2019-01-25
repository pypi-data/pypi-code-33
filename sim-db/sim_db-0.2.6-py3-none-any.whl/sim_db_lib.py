# -*- coding: utf-8 -*-
"""Read and write parameters, results and metadata to the 'sim_db' database."""
# Copyright (C) 2017-2019 Håkon Austlid Taskén <hakon.tasken@gmail.com>
# Licenced under the MIT License.

import sim_db.src_command_line_tool.commands.helpers as helpers
import sqlite3
import argparse
import subprocess
import time
import hashlib
import threading
import os
import sys


class SimDB:
    """To interact with the **sim_db** database.

    For an actuall simulation it should be initialised at the very start of the 
    simulation (with 'store_metadata' set to True) and closed with 
    :func:`~SimDB.close` at the very end of the simulation. This must be done 
    to add the corrrect metadata.

    For multithreading/multiprocessing each thread/process MUST have its
    own connection (instance of this class).
    """

    def __init__(self, store_metadata=True, db_id=None):
        """Connect to the **sim_db** database.

        :param store_metadata: If False, no metadata is added to the database.
            Typically used when postprocessing (visualizing) data from a
            simulation.
        :type store_metadata: bool
        :param db_id: ID number of the simulation parameters in the **sim_db**
            database. If it is 'None', then it is read from the argument passed
            to the program after option '--id'.
        :type db_id: int
        """
        self.start_time = time.time()
        self.store_metadata = store_metadata
        self.id, self.path_proj_root = self.__read_from_command_line_arguments(
                db_id)
        self.db = helpers.connect_sim_db()
        self.db_cursor = self.db.cursor()
        self.column_names = []
        self.column_types = []

        if self.store_metadata:
            try:
                self.write('status', 'running', only_if_empty=True)
                self.write(
                        'time_started',
                        self.__get_date_and_time_as_string(),
                        only_if_empty=True)
            except sqlite3.OperationalError:
                pass

        if self.store_metadata and self.__is_a_git_project():
            proc = subprocess.Popen(
                    [
                            'cd "{0}"; git rev-parse HEAD'.format(
                                    self.path_proj_root)
                    ],
                    stdout=subprocess.PIPE,
                    stderr=open(os.devnull, 'w'),
                    shell=True)
            (out, err) = proc.communicate()
            try:
                self.write(
                        column="git_hash",
                        value=out.decode('ascii', 'replace'),
                        only_if_empty=True)
            except sqlite3.OperationalError:
                pass

            proc = subprocess.Popen(
                    [
                            'cd "{0}"; git log -n 1 --format=%B HEAD'.format(
                                    self.path_proj_root)
                    ],
                    stdout=subprocess.PIPE,
                    stderr=open(os.devnull, 'w'),
                    shell=True)
            (out, err) = proc.communicate()
            try:
                self.write(
                        column="commit_message",
                        value=out.decode('ascii', 'replace'),
                        only_if_empty=True)
            except sqlite3.OperationalError:
                pass

            proc = subprocess.Popen(
                    [
                            'cd "{0}"; git diff HEAD --stat'.format(
                                    self.path_proj_root)
                    ],
                    stdout=subprocess.PIPE,
                    stderr=open(os.devnull, 'w'),
                    shell=True)
            (out, err) = proc.communicate()
            try:
                self.write(
                        column="git_diff_stat",
                        value=out.decode('ascii', 'replace'),
                        only_if_empty=True)
            except sqlite3.OperationalError:
                pass

            proc = subprocess.Popen(
                    ['cd "{0}"; git diff HEAD'.format(self.path_proj_root)],
                    stdout=subprocess.PIPE,
                    stderr=open(os.devnull, 'w'),
                    shell=True)
            (out, err) = proc.communicate()
            out = out.decode('ascii', 'replace')
            if len(out) > 3000:
                warning = "WARNING: Diff limited to first 3000 characters.\n"
                out = warning + '\n' + out[0:3000] + '\n\n' + warning
            try:
                self.write(column="git_diff", value=out, only_if_empty=True)
            except sqlite3.OperationalError:
                pass

    def read(self, column, check_type_is=''):
        """Read parameter in 'column' from the database.

        Return None if parameter is empty.

        :param column: Name of the column the parameter is read from.
        :type column: str
        :param check_type_is: Throws ValueError if type does not match 
            'check_type_is'.The valid types the strings 'int', 'float', 'bool',
            'string' and 'int/float/bool/string array' or the types int, float, 
            bool, str and list.
        :raises ColumnError: If column do not exists.
        :raises ValueError: If return type does not match 'check_type_is'.
        :raises sqlite3.OperationalError: Waited more than 5 seconds to read 
            from the database, because other threads/processes are busy writing 
            to it. Way too much concurrent writing is done and it indicates an 
            design error in the user program.
        """

        if column not in self.column_names:
            self.column_names, self.column_types = (
                    helpers.get_db_column_names_and_types(self.db_cursor))
            if column not in self.column_names:
                raise ColumnError("Column, {0}, is NOT a column in the "
                                  "database.".format(column))
        self.db_cursor.execute("SELECT {0} FROM runs WHERE id={1}".format(
                column, self.id))
        value = self.db_cursor.fetchone()
        if value != None:
            value = value[0]
            value = self.__check_type(check_type_is, column, self.column_names,
                                      self.column_types, value)

        return value

    def write(self, column, value, type_of_value='', only_if_empty=False):
        """Write value to 'column' in the database.

        If 'column' does not exists, a new is added.

        If value is None and type_of_value is not set, the entry under 'column'
        is set to empty.

        :param column: Name of the column the parameter is read from.
        :type column: str
        :param value: New value of the specified entry in the database.
        :param type_of_value: Needed if column does note exists or if
            value is empty list. The valid types the strings 'int', 'float',
            'bool', 'string' and 'int/float/bool/string array' or the types int,
            float, bool and str.
        :type type_of_value: str or type
        :param only_if_empty: If True, it will only write to the database if the
            simulation's entry under 'column' is empty. Will avoid any possible 
        :type only_if_empty: bool
        :raises ValueError: If column exists, but type does not match, or 
            empty list is passed without type_of_value given.
        :raises sqlite3.OperationalError: Waited more than 5 seconds to write
            to the database, because other threads/processes are busy writing 
            to it. Way too much concurrent writing is done and it indicates an 
            design error in the user program.
        """

        self.__add_column_if_not_exists_and_check_type(column, type_of_value,
                                                       value)

        value_string = self.__convert_to_value_string(value, type_of_value)
        value_string = self.__escape_quote_with_two_quotes(value_string)
        type_dict = dict(zip(self.column_names, self.column_types))
        # 'and type(value != None) != bool' allow numpy arrays to be check
        # without importing numpy and thereby relying on it being availble.
        if (type_dict[column] == 'TEXT' 
                and (type(value != None) != bool or value != None)):
            value_string = "'{0}'".format(value_string)
        if only_if_empty:
            is_busy = True
            start_time = time.time()
            while is_busy:
                is_busy = False
                is_empty = self.is_empty(column)
                if is_empty:
                    self.db_cursor.execute("PRAGMA busy_timeout=0")
                    self.db.commit()
                    try:
                        self.db_cursor.execute(
                                "UPDATE runs SET \"{0}\" = {1} WHERE \"id\" = "
                                "{2} AND {0} IS NULL".format(
                                        column, value_string, self.id))
                        self.db.commit()
                    except sqlite3.OperationalError:
                        is_busy = True
                        if time.time() > start_time + 5.0:
                            self.db_cursor.execute("PRAGMA busy_timeout=5000")
                            self.db.commit()
                            raise
                self.db_cursor.execute("PRAGMA busy_timeout=5000")
                self.db.commit()
        else:
            self.db_cursor.execute(
                    "UPDATE runs SET \"{0}\" = {1} WHERE id = {2}".format(
                            column, value_string, self.id))
            self.db.commit()

    def unique_results_dir(self, path_directory):
        """Get path to subdirectory in 'path_directory' unique to simulation.

        The subdirectory will be named 'date_time_name_id' and is intended to
        store results in. If 'results_dir' in the database is empty, a new and 
        unique directory is created and the path stored in 'results_dir'. 
        Otherwise the path in 'results_dir' is just returned.

        :param path_directory: Path to directory of which to make a 
            subdirectory. If 'path_directory' starts with 'root/', that part 
            will be replaced by the full path of the root directory of the 
            project.
        :type path_directory: str
        :returns: Full path to new subdirectory.
        :rtype: str
        :raises sqlite3.OperationalError: Waited more than 5 seconds to write
            to the database, because other threads/processes are busy writing 
            to it. Way too much concurrent writing is done and it indicates an 
            design error in the user program.
        """
        results_dir = self.read("results_dir")
        if (
                results_dir != None
                and results_dir[0:32] != "results_dir_is_currenty_made_by_"):
            return results_dir

        unique_process_thread_name = ("results_dir_is_currenty_made_by_" + str(
                os.getpid()) + "_" + str(threading.current_thread().ident))

        self.write(
                "results_dir", unique_process_thread_name, only_if_empty=True)

        results_dir = self.read("results_dir")
        if results_dir == unique_process_thread_name:
            if (len(path_directory) >= 5 and path_directory[0:5] == 'root/'):
                path_directory = os.path.join(self.path_proj_root,
                                              path_directory[5:])
            results_dir = os.path.join(path_directory,
                                       self.__get_date_and_time_as_string())
            results_dir += '_' + self.read('name') + '_' + str(self.id)
            results_dir = os.path.abspath(os.path.realpath(results_dir))
            os.mkdir(results_dir)
            self.write(
                    column="results_dir",
                    value=results_dir,
                    only_if_empty=False)
        else:
            while results_dir[0:32] == "results_dir_is_currenty_made_by_":
                results_dir = self.read("results_dir")

        return results_dir

    def column_exists(self, column):
        """Return True if column is a column in the database.

        :raises sqlite3.OperationalError: Waited more than 5 seconds to read
            from the database, because other threads/processes are busy writing 
            to it. Way too much concurrent writing is done and it indicates an 
            design error in the user program.
        """
        if column in self.column_names:
            return True
        else:
            self.column_names, self.column_types = (
                    helpers.get_db_column_names_and_types(self.db_cursor))
            if column in self.column_names:
                return True
            else:
                return False

    def is_empty(self, column):
        """Return True if entry in the database under 'column' is empty.

        :raises sqlite3.OperationalError: Waited more than 5 seconds to read
            from the database, because other threads/processes are busy writing 
            to it. Way too much concurrent writing is done and it indicates an 
            design error in the user program.
        """
        value = self.read(column)
        if value == None:
            return True
        else:
            return False

    def set_empty(self, column):
        """Set entry under 'column' in the database to empty.

        :raises sqlite3.OperationalError: Waited more than 5 seconds to write
            to the database, because other threads/processes are busy writing 
            to it. Way too much concurrent writing is done and it indicates an 
            design error in the user program.
        """
        self.write(column, None)

    def get_id(self):
        """Return 'ID' of the connected simulation."""
        return self.id

    def get_path_proj_root(self):
        """Return the path to the root directory of the project.

        The project's root directory is assumed to be where the '.sim_db/'
        directory is located.
        """
        return self.path_proj_root

    def update_sha1_executables(self, paths_executables):
        """Update the 'sha1_executable' column in the database.

        Sets the entry to the sha1 of all the executables. The order will
        affect the value.

        :param paths_executables: List of full paths to executables.
        :type paths_executables: [str]
        :raises sqlite3.OperationalError: Waited more than 5 seconds to write
            to the database, because other threads/processes are busy writing 
            to it. Way too much concurrent writing is done and it indicates an 
            design error in the user program.
        """
        sha1 = hashlib.sha1()
        for executable in executables:
            with open(executable, 'r') as executable_file:
                sha1.update(executable_file.read())
        try:
            self.write('sha1_executables', sha1)
        except sqlite3.OperationalError:
            pass

    def delete_from_database(self):
        """Delete simulation from database.

        :raises sqlite3.OperationalError: Waited more than 5 seconds to write
            to the database, because other threads/processes are busy writing 
            to it. Way too much concurrent writing is done and it indicates an 
            design error in the user program.
        """
        self.db_cursor.execute("DELETE FROM runs WHERE id = {0}".format(
                self.id))
        self.db.commit()
        self.store_metadata = False

    def close(self):
        """Closes connection to **sim_db** database and add metadata."""
        if self.store_metadata:
            used_time = time.time() - self.start_time
            used_walltime = "{0}h {1}m {2}s".format(
                    int(used_time / 3600), int(used_time / 60), used_time % 60)
            try:
                self.write('used_walltime', used_walltime, only_if_empty=True)
                self.write('status', 'finished')
            except sqlite3.OperationalError:
                pass
        self.db_cursor.close()
        self.db.close()

    def __read_from_command_line_arguments(self, db_id):
        path_proj_root = None
        if db_id == None:
            parser = argparse.ArgumentParser()
            parser.add_argument(
                    '--id',
                    '-i',
                    type=int,
                    default=None,
                    required=True,
                    help=("<Required> ID of parameters in the database used "
                          "to run the simulation."))
            parser.add_argument(
                    '--path_proj_root',
                    '-p',
                    type=str,
                    default=None,
                    help="Path to the root directory of the project.")
            args, unknowns = parser.parse_known_args()
            db_id = args.id
            if args.path_proj_root != None:
                path_proj_root = os.path.abspath(args.path_proj_root)
        if (path_proj_root == None):
            path_proj_root = os.path.dirname(helpers.get_dot_sim_db_dir_path())
        else:
            if path_proj_root[-1] == '/':
                path_proj_root = path_proj_root[:-1]
        if (db_id == None):
            ValueError("'db_id' is NOT provided to SimDB(db_id=None). If not "
                       "passed as function parameters, then '--id ID' must be "
                       "passed to program as command line arguments.")
        return (db_id, path_proj_root)

    def __check_type(self,
                     check_type_is,
                     column,
                     column_names,
                     column_types,
                     value=None):
        type_dict = dict(zip(column_names, column_types))
        type_of_value = type_dict[column]

        if ((check_type_is == 'int' or check_type_is == int)
                    and type_of_value == 'INTEGER'):
            correct_type = True
            if value != None:
                try:
                    int(value)
                except:
                    correct_type = False
        elif ((check_type_is == 'float' or check_type_is == float)
              and type_of_value == 'REAL'):
            correct_type = True
            if value != None:
                try:
                    float(value)
                except:
                    correct_type = False
        # 'type(value != None) != bool' allow numpy arrays to be check
        # without importing numpy and thereby relying on it being availble.
        elif (type_of_value == 'TEXT'
              and (type(value != None) != bool or value != None)):
            if type(value) == str:
                value, correct_type = self.__convert_text_to_correct_type(
                        value, check_type_is)
            elif type(value) == bool:
                correct_type = True
            elif check_type_is == 'bool' or check_type_is == bool:
                try:
                    value = bool(value)
                    correct_type = True
                except ValueError:
                    correct_type = False
            else:
                try:
                    value = list(value)
                    correct_type = True
                except TypeError:
                    correct_type = False
        # 'and type(value != None) == bool' allow numpy arrays to be check
        # without importing numpy and thereby relying on it being availble.
        elif (type_of_value == 'TEXT' 
              and (type(value == None) == bool and value == None)
              and (check_type_is == 'string' or check_type_is == str
                   or check_type_is == 'bool' or check_type_is == bool
                   or check_type_is == list or check_type_is == 'int array'
                   or check_type_is == 'float array'
                   or check_type_is == 'bool array'
                   or check_type_is == 'string array')):
            correct_type = True
        else:
            correct_type = False

        if not correct_type and check_type_is != '':
            raise ValueError("The type is NOT {0}.".format(check_type_is))

        return value

    def __convert_text_to_correct_type(self, value, check_type_is):
        correct_type = False
        value_split = value.split('[')
        if value == "True":
            value = True
            if (check_type_is == 'bool' or check_type_is == bool):
                correct_type = True
        elif value == "False":
            value = False
            if (check_type_is == 'bool' or check_type_is == bool):
                correct_type = True
        elif len(value_split) == 1:
            if (check_type_is == 'string' or check_type_is == str):
                correct_type = True
        else:
            value = []
            if value_split[0].strip() == 'int':
                if (check_type_is == 'int array' or check_type_is == list):
                    correct_type = True
                for element in value_split[1].split(']')[0].split(','):
                    value.append(int(element))
            elif value_split[0].strip() == 'float':
                if (check_type_is == 'float array' or check_type_is == list):
                    correct_type = True
                for element in value_split[1].split(']')[0].split(','):
                    value.append(float(element))
            elif value_split[0].strip() == 'string':
                if (check_type_is == 'string array' or check_type_is == list):
                    correct_type = True
                for i, element in enumerate(
                        value_split[1].split(']')[0].split(',')):
                    if i > 0 and len(element) > 0 and element[0] == ' ':
                        element = element[1:]
                    value.append(str(element))
            elif value_split[0].strip() == 'bool':
                if (check_type_is == 'bool array' or check_type_is == list):
                    correct_type = True
                for i, element in enumerate(
                        value_split[1].split(']')[0].split(',')):
                    if i > 0 and len(element) > 0 and element[0] == ' ':
                        element = element[1:]
                    if element == 'True':
                        element = True
                    elif element == 'False':
                        element = False
                    else:
                        correct_type = False
                    value.append(element)
            else:
                if (check_type_is == 'string' or check_type_is == str):
                    correct_type = True
                else:
                    correct_type = False
        return value, correct_type

    def __convert_to_value_string(self, value, type_of_value):
        if sys.version_info[0] < 3 and type(value) == unicode:
            return value.encode('ascii', 'replace')
        elif (type(value) == int or type(value) == float or type(value) == str
                or type_of_value == 'int' or type_of_value == int
                or type_of_value == 'float' or type_of_value == float
                or type_of_value == 'string' or type_of_value == str):
            return str(value)
        elif type(value) == bool:
            if value:
                return "True"
            else:
                return "False"
        # 'type(value == None) == bool' allow numpy arrays to be check
        # without importing numpy and thereby relying on it being availble.
        elif (type(value == None) == bool and value == None):
            return "NULL"
        else:
            try:
                value = list(value)
            except TypeError:
                raise ValueError("'value' have invalid type.")
            if len(value) > 0:
                if type_of_value == 'int array' or type(value[0]) == int:
                    value_string = "int["
                elif type_of_value == 'float array' or type(value[0]) == float:
                    value_string = "float["
                elif type_of_value == 'string array' or type(value[0]) == str:
                    value_string = "string["
                elif type_of_value == 'bool array' or type(value[0]) == bool:
                    value_string = "bool["
                for element in value:
                    if type(value[0]) == bool:
                        if element:
                            element = "True"
                        else:
                            element = "False"
                    value_string += str(element) + ", "
                value_string = value_string[:-2] + "]"
                return value_string
            else:
                if type_of_value == 'int array':
                    value_string = "int[]"
                elif type_of_value == 'float array':
                    value_string = "float[]"
                elif type_of_value == 'string array':
                    value_string = "string[]"
                elif type_of_value == 'bool array':
                    value_string = "bool[]"
                else:
                    raise ValueError(
                            "The type_of_value must be set to 'int array', "
                            "'float array', 'string array' or 'bool array' "
                            "when a empty list is passed to SimDB.write().")
                return value_string

    def __add_column(self, column, type_of_value):
        if type_of_value == '':
            print("ERROR: Column {0} does not exists in database and "
                  "'type_of_value' must be provided for it to be added."
                  .format(column))
            exit(1)
        start_time = time.time()
        is_busy = True
        self.db_cursor.execute("PRAGMA busy_timeout=0")
        while is_busy:
            is_busy = False
            try:
                if type_of_value == 'int' or type_of_value == int:
                    self.db_cursor.execute(
                            "ALTER TABLE runs ADD COLUMN {0} INTEGER".format(
                                    column))
                elif type_of_value == 'float' or type_of_value == float:
                    self.db_cursor.execute(
                            "ALTER TABLE runs ADD COLUMN {0} REAL".format(
                                    column))
                else:
                    self.db_cursor.execute(
                            "ALTER TABLE runs ADD COLUMN {0} TEXT".format(
                                    column))
                self.db.commit()
            except sqlite3.OperationalError as e:
                if str(e)[0:12] == "duplicate column name:":
                    is_busy = False
                else:
                    is_busy = True
                if time.time() > start_time + 5.0:
                    self.db_cursor.execute("PRAGMA busy_timeout=5000")
                    raise
        self.db_cursor.execute("PRAGMA busy_timeout=5000")

    def __add_column_if_not_exists_and_check_type(self, column, type_of_value,
                                                  value):
        if column in self.column_names:
            self.__check_type(type_of_value, column, self.column_names,
                              self.column_types, value=value)
        else:
            self.column_names, self.column_types = (
                    helpers.get_db_column_names_and_types(self.db_cursor))
            if column in self.column_names:
                self.__check_type(type_of_value, column, self.column_names,
                                  self.column_types, value=value)
            else:
                if (type_of_value == 'int' or type_of_value == int):
                    column_type = 'INTEGER'
                elif (type_of_value == 'float' or type_of_value == float):
                    column_type = 'REAL'
                else:
                    column_type = 'TEXT'
                self.__check_type(
                        type_of_value,
                        column, [column], [column_type],
                        value=value)
                self.__add_column(column, type_of_value)
                self.column_names, self.column_types = (
                        helpers.get_db_column_names_and_types(self.db_cursor))

    def __is_a_git_project(self):
        directory = self.path_proj_root
        prev_dir = ""
        while directory != prev_dir:
            if os.path.exists(os.path.join(directory, ".git")):
                return True
            prev_dir = directory
            directory = os.path.dirname(directory)
        return False

    def __escape_quote_with_two_quotes(self, string):
        escaped_string = ""
        for letter in string:
            if letter == "'":
                escaped_string += "''"
            else:
                escaped_string += letter
        return escaped_string

    def __get_date_and_time_as_string(self):
        """Return data and time as 'Year-Month-Date_Hours-Minutes-Seconds'."""
        return time.strftime("%Y-%b-%d_%H-%M-%S")


class ColumnError(Exception):
    pass


def add_empty_sim(store_metadata=False):
    """Add an empty entry into the database and SimDB connected to it.

    :param store_metadata: If False, no metadata is added to the database.
        Typically used when postprocessing (visualizing) data from a simulation.
    :type store_metadata: bool
    """
    db = helpers.connect_sim_db()
    db_cursor = db.cursor()
    default_db_columns = ""
    for key in helpers.default_db_columns:
        default_db_columns += key + " " + str(
                helpers.default_db_columns[key]) + ", "
    default_db_columns = default_db_columns[:-2]
    db_cursor.execute("CREATE TABLE IF NOT EXISTS runs ({0});".format(
            default_db_columns))
    db_cursor.execute("INSERT INTO runs DEFAULT VALUES")
    db_id = db_cursor.lastrowid
    db.commit()
    db_cursor.close()
    db.close()

    return SimDB(db_id=db_id, store_metadata=store_metadata)
