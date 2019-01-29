#!/usr/bin/env python
import sys
import MySQLdb
import vmtools
import collections
from time import sleep
from collections import OrderedDict
from deepdiff import DeepDiff
import re

vm_root_path = vmtools.vm_root_grabber()
sys.path.append(vm_root_path)
#from local_settings import *

class QuickMysql():
    """A class simplify common mysql tasks

    instance variables:
    self.placeholder
    """

    def __init__(self, dbhost, dbuser, dbpass, dbname=None, dbport=3306):
        """set instance variables, set instance aws connections

        keyword arguments:
        :type dbhost: string
        :param dbhost: the hostname of the mysql server
        :type dbuser: string
        :param dbuser: the username to use to connect to the mysql server
        :type dbpass: string
        :param dbpass: the password for dbuser
        :type dbname: string
        :param dbname: the name of the database to connect to
        :type dbport: int
        :param dbport: the port to connect to
        """
        self.dbhost = dbhost
        self.dbuser = dbuser
        self.dbpass = dbpass
        self.dbname = dbname
        self.dbport = dbport


    def connect_to_database(self, dbhost=None, dbuser=None, dbpass=None, dbname=None, dbport=None, num_of_tries=5):
        """Creates a connection to the database, returns the cursor object
        keyword arguments:
        :type dbhost: string
        :param dbhost: the hostname of the mysql server
        :type dbuser: string
        :param dbuser: the username to use to connect to the mysql server
        :type dbpass: string
        :param dbpass: the password for dbuser
        :type dbname: string
        :param dbname: the name of the database to connect to
        :type dbport: int
        :param dbport: the port to connect to
        :type num_of_tries: int
        :param num_of_tries: the number of tries to attempt to connect to the database server
        """
        dbhost = dbhost if dbhost is not None else self.dbhost
        dbuser = dbuser if dbuser is not None else self.dbuser
        dbpass = dbpass if dbpass is not None else self.dbpass
        dbname = dbname if dbname is not None else self.dbname
        dbport = dbport if dbport is not None else self.dbport
        actual_tries = 0
        while actual_tries < num_of_tries:
            try:
                con = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbname, port=dbport)
                break
            except MySQLdb._exceptions.OperationalError as err:
                print('Tries: ', actual_tries)
                sleep(3)
                actual_tries +=1
                if actual_tries == num_of_tries:
                    raise MySQLdb._exceptions.OperationalError(err)
        cur = con.cursor()
        return(cur, con)

    def connect_to_mysql(self, dbhost=None, dbuser=None, dbpass=None, dbport=None):
        """Creates a connection to the database, returns the cursor object
        """
        dbhost = dbhost if dbhost is not None else self.dbhost
        dbuser = dbuser if dbuser is not None else self.dbuser
        dbpass = dbpass if dbpass is not None else self.dbpass
        dbport = dbport if dbport is not None else self.dbport
        con = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpass, port=dbport)
        cur = con.cursor()
        return(cur, con)


    def does_user_exist(self, dbuser, dbhost, dbpass, dbport=3306):
        # try to connect as user
        try:
            MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpass, port=dbport)
        except MySQLdb._exceptions.OperationalError:
            return False
        else:
            return True

    def column_as_list(self, table_name, column_name, start_date=None, end_date=None, timestamp_column_name='timestamp'):
        """Return data from column as a list
        keyword arguments:
        :type table_name: string
        :param table_name: the name of the mysql table
        :type column_name: string
        :param column_name: the name of the column
        :type start_date: string
        :param start_date: (NOTE: to use this option table must have a timestamp column and you must timestamp_column_name) the start date for the time range in the format strftime("%Y-%m-%d %H:%M:%S") (example "2018-03-29 12:00:00") a value of None means no start_date
        :type end_date: string
        :param end_date: (NOTE: to use this option table must have a timestamp column and you must timestamp_column_name) the end date for the time range in the format strftime("%Y-%m-%d %H:%M:%S") (example "2018-03-29 12:00:00") a value of None means no end_date
        :type timestamp_column_name: string
        :param timestamp_column_name: (NOTE: this argument must be set if either start_date or end_date is set) the name of the timestamp column 
        """
        # connect to database
        cur, con = self.connect_to_database()
        if start_date or end_date:
            if start_date and not end_date:
                sql_cmd = "select {} from {} WHERE {} >= '{}'".format(column_name, table_name, timestamp_column_name, start_date)
            elif end_date and not start_date:
                sql_cmd = "select {} from {} WHERE {} <= '{}'".format(column_name, table_name, timestamp_column_name, end_date)
            elif start_date and end_date:
                sql_cmd = "select {} from {} WHERE {} >= '{}' and {} <= '{}'".format(column_name, table_name, timestamp_column_name, start_date, timestamp_column_name, end_date)
        else:
            sql_cmd = 'select {} from {}'.format(column_name, table_name)
        cur.execute(sql_cmd)
        output = cur.fetchall()
        column_list = [ innertuple[0] for innertuple in output ]
        # close connection
        self.close_database_connection(connection_object=con)
        return column_list

    def row_as_dict(self, table_name, sql_cmd):
        """Take table_name and sql_cmd and return a dict from the returned row (sql_cmd must return all columns and only one row)
        keyword arguments:
        :type sql_cmd: str
        :param sql_cmd: the sql to execute (sql_cmd must return all columns and only one row)
        :type table_name: string
        :param table_name: the name of the mysql table
        """
        cur, con = self.connect_to_database()
        row_dict = {}
        # get column names
        column_names_sql = "select column_name from information_schema.columns where table_name = '{}' AND table_schema = '{}'".format(table_name, self.dbname)
        cur.execute(column_names_sql)
        column_names_tuple_of_tuples = cur.fetchall()
        cur.execute(sql_cmd)
        output = cur.fetchall()
        # if no output return empty row_dict
        if output:
            if len(output[0]) == len(column_names_tuple_of_tuples):
                for index_number, value in enumerate(column_names_tuple_of_tuples):
                    row_dict[value[0]] = output[0][index_number]
            else:
                raise ValueError('The sql_cmd given did not return the the same number of columns as there are in the table.')
            # close connection
            self.close_database_connection(connection_object=con)
        return row_dict

    def table_defition_as_ordereddict(self, table_name):
        """
        Take table_name return an oridered dict from the table defition
        keyword arguments:
        :type table_name: str
        :param table_name: the name of the table
        """
        show_create_table_cmd = 'SHOW CREATE TABLE {}'.format(table_name)
        show_create_table_cmd_output = self.execute_simple(sql_cmd=show_create_table_cmd)
        table_raw_column_list = show_create_table_cmd_output[0][1].split('(\n')[1].split('\n)')[0].split(',\n  ')
        table_defition_ordereddict = OrderedDict([ (table_raw_column_list[idx].split('`')[1],table_raw_column_list[idx].split('`')[2].lstrip() ) for idx, val in enumerate(table_raw_column_list)])
        return table_defition_ordereddict

    def get_dict_of_table_defitions_for_database(self, table_names_list=[]):
        """
        Return a dict of defitions for the current database
        :type table_names_list: list
        :param table_names_list: (optional) limit to only these tables
        """
        table_defitions_dict = {}
        show_tables_sql = 'show tables'
        show_tables_output = self.execute_simple(sql_cmd=show_tables_sql)
        if table_names_list:
            for table_tuple in show_tables_output:
                if table_tuple[0] in table_names_list:
                    table_defitions_dict[table_tuple[0]] = self.table_defition_as_ordereddict(table_name=table_tuple[0])
        else:
            for table_tuple in show_tables_output:
                table_defitions_dict[table_tuple[0]] = self.table_defition_as_ordereddict(table_name=table_tuple[0])
        return table_defitions_dict

    def close_database_connection(self, connection_object):
        """
        Close the database connection
        """
        connection_object.commit()
        connection_object.close()

    def create_database_user(self, dbuser, dbpass, dbname, dbhost='localhost', privileges_list=[]):
        """
        Take dbuser, dbname, dbpass, host, and optionally privileges_list and create a db user
        keyword arguments:
        :type dbuser: string
        :param dbuser: the username to use to connect to the mysql server
        :type dbpass: string
        :param dbpass: the password for dbuser
        :type dbname: string
        :param dbname: the name of the database to connect to
        :type dbhost: string
        :param dbhost: the hostname of the mysql server, defaults to 'localhost'
        :type privileges_list: list
        :param privileges_list: optional a list of privileges to assign to the user (ex: ['select', 'update', 'insert']), defaults to 'all privileges'
        """
        # connect to mysql
        cur, con = self.connect_to_mysql()
        # create user
        check_existence_user_cmd = "SELECT * FROM mysql.user WHERE user = '{}'".format(dbuser)
        check_existence_user_result = cur.execute(check_existence_user_cmd)
        if privileges_list:
            privileges_str = ' '.join(privileges_list)
        else:
            privileges_str = 'all privileges'
        if check_existence_user_result == 0:
            mysql_create_user_cmd = "grant {} on {}.* to '{}'@'{}' identified by '{}'".format( privileges_str, dbname, dbuser, dbhost, dbpass)
            cur.execute(mysql_create_user_cmd)
        # close connection
        self.close_database_connection(connection_object=con)

    def create_database(self, dbname):
        """Creates an empty database 
        """
        # connect to mysql
        cur, con = self.connect_to_mysql()
        # create db
        check_existence_database_cmd = "SHOW DATABASES LIKE '{}'".format(dbname)
        check_existence_database_result = cur.execute(check_existence_database_cmd)
        if check_existence_database_result == 0:
            mysql_create_db_cmd = 'create database if not exists {}'.format(dbname)
            cur.execute(mysql_create_db_cmd)
        # close connection
        self.close_database_connection(connection_object=con)

    def execute_simple(self, sql_cmd):
        """Take sql_cmd, execute and return the output
        keyword arguments:
        :type sql_cmd: str
        :param sql_cmd: the sql to execute
        """
        # connect to database
        cur, con = self.connect_to_database()
        cur.execute(sql_cmd)
        output = cur.fetchall()
        # close connection
        self.close_database_connection(connection_object=con)
        return output

    def execute_simple_generator(self, sql_cmd, batch_size=1000):
        """Take sql_cmd, execute as an iterator that fetches batch_size records at a time to keep memory usage low
        keyword arguments:
        :type sql_cmd: str
        :param sql_cmd: the sql to execute
        :type batch_size: int
        :param batch_size: the number of records to fetch in each batch
        """
        # connect to database
        cur, con = self.connect_to_database()
        # execute sql
        cur.execute(sql_cmd)
        # grab records in batches
        while True:
            current_batch = cur.fetchmany(batch_size)
            if not current_batch:
                # if no more records close connection and break out of while loop
                self.close_database_connection(connection_object=con)
                break
            for record in current_batch:
                yield record

    def execute_many(self, sql_cmd, input_sequence):
        """Loop through sequence and execute sql_cmd
        keyword arguments:
        :type sql_cmd: str
        :param sql_cmd: the sql to execute
        :type input_sequence: list or tuple
        :param input_sequence: sequence of sequences (ex [[1,2], [3, 4], [5,6]])
        """
        # connect to database
        cur, con = self.connect_to_database()
        cur.executemany(sql_cmd, input_sequence)
        output = cur.fetchall()
        # close connection
        self.close_database_connection(connection_object=con)
        return output

    def is_legal_mysql_table_name(self, table_name):
        """
        Takes a table_name determines if the name is legal for MySql
        :type table_name: str
        :param table_name: the name for the table
        """
        legal_mysql_table_name_regex_object = re.compile(r'[^a-zA-Z0-9_$.]')
        legal_mysql_table_name_regex_search_result = legal_mysql_table_name_regex_object.search(table_name)
        if bool(legal_mysql_table_name_regex_search_result):
            table_name_not_legal_message = 'The table name {} is not a MySql legal table name. Only the following characters are allowed [a-zA-Z0-9_$]'.format(table_name)
            print(table_name_not_legal_message)
            sys.exit(1)
        return True

    def create_table(self, table_name, column_dict):
        """
        Takes a table_name and column_dict, creates a table
        :type table_name: str
        :param table_name: the name for the table
        :type column_dict: dict
        :param column_dict: a ordered dictionary, created by using collections.OrderedDict() and passing it a list of two item tuples (first item is key, second is value), ex collections.OrderedDict([('order_id', 'bigint(50)'), ('trade_id', 'bigint(50)')]); this is essential to ensure the order of the columns
        """
        # connect to database
        self.is_legal_mysql_table_name(table_name)
        cur, con = self.connect_to_database()
        check_existence_table_cmd = "SHOW TABLES LIKE '{}'".format(table_name)
        check_existence_result = cur.execute(check_existence_table_cmd)
        if check_existence_result == 0:
            columns_definitions = ', '.join("{!s} {!s}".format(key,val) for (key,val) in column_dict.items())
            mysql_create_table_cmd = "create table if not exists {} ( {} )".format(table_name, columns_definitions)
            cur.execute(mysql_create_table_cmd)
        # close connection
        self.close_database_connection(connection_object=con)

    def create_tables_from_table_defition_dict(self, table_defitions_dict):
        """
        Takes a table_defitions_dict, creates tables defined in table_defitions_dict
        :type table_defitions_dict: dict
        :param table_defitions_dict: a dict of ordereddicts with the keys being the name of the table as generated by the function get_dict_of_table_defitions_for_database
        """
        for table_name in table_defitions_dict.keys():
            self.create_table(table_name=table_name, column_dict=table_defitions_dict[table_name])
        

    def update_table(self, table_name, new_column_dict):
        """Takes a table_name and new_column_dict and updates the existing table to match new_column_dict
        :type table_name: str
        :param table_name: the name for the table
        :type new_column_dict: dict
        :param new_column_dict: a ordered dictionary, created by using collections.OrderedDict() and passing it a list of two item tuples (first item is key, second is value), ex collections.OrderedDict([('order_id', 'bigint(50)'), ('trade_id', 'bigint(50)')]); this is essential to ensure the order of the columns
        """
        current_table_defition_ordereddict = self.table_defition_as_ordereddict(table_name=table_name)
        table_diff = DeepDiff(current_table_defition_ordereddict, new_column_dict, verbose_level=2)
        # loop through and add all new columns
        while 'dictionary_item_added' in table_diff: 
            new_column_name = list(table_diff['dictionary_item_added'].keys())[0].split("'")[1]
            new_column_defition = table_diff['dictionary_item_added'][list(table_diff['dictionary_item_added'].keys())[0]]
            add_column_sql = "alter table {} add {} {}".format(table_name, new_column_name, new_column_defition)
            self.execute_simple(sql_cmd=add_column_sql)
            current_table_defition_ordereddict = self.table_defition_as_ordereddict(table_name=table_name)
            table_diff = DeepDiff(current_table_defition_ordereddict, new_column_dict, verbose_level=2)
        # loop through and drop all deleted columns
        while 'dictionary_item_removed' in table_diff: 
            column_name = list(table_diff['dictionary_item_removed'].keys())[0].split("'")[1]
            drop_column_sql = "alter table {} drop {}".format(table_name, column_name)
            self.execute_simple(sql_cmd=drop_column_sql)
            current_table_defition_ordereddict = self.table_defition_as_ordereddict(table_name=table_name)
            table_diff = DeepDiff(current_table_defition_ordereddict, new_column_dict, verbose_level=2)
        # loop through and change all changed columns, but not with while because certain default parts of defitions would cause infinite loops
        if 'values_changed' in table_diff: 
            for column in table_diff['values_changed']:
                if table_diff['values_changed'][column]['old_value'].upper() != table_diff['values_changed'][column]['new_value'].upper():
                    column_name = column.split("'")[1]
                    new_column_defition = table_diff['values_changed'][column]['new_value']
                    modify_column_sql = "alter table {} modify {} {}".format(table_name, column_name, new_column_defition)
                    self.execute_simple(sql_cmd=modify_column_sql)
            table_diff.pop('values_changed', None)
        if table_diff:
            print(table_diff)
            raise ValueError('the dictionary table_diff from function update_table from library quickmysql should be empty at this point, but it is not. This bug should be investigated. Above is the table_diff dict.')

