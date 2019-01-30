import pandas as pd
import logging
import os
import contextlib
import csv
import datetime

logger = logging.getLogger("dativa.tools.sql_client")


class SqlClient:
    """
    A wrapper for PEP249 connection objects to provide additional logging and simple execution
    of queries and optional writing out of results to DataFrames or CSV

    The client runs mult-statement SQL queries from file or from strings and can return the
    result of the final SQL statement in either a DataFrame or as a CSV

    Parameters:
    - db_connection - a connection object from a PEP249 compliant class
    """

    def __init__(self, db_connection):

        self.connection = db_connection
        self.cursor = self.connection.cursor()

    def _prepare_sql(self, query, parameters):
        # replace any parameters
        new_query = query.format(**parameters)

        return new_query.split(";")

    def _print_query(self, query, parameters):
        logger.info("#EXECUTING QUERY @{0}".format(datetime.datetime.now()))
        logger.info("#PARAMETERS {0}".format(parameters))
        i = 1
        for line in query.split("\n"):
            if i < 5:
                logger.info("{0:03} {1}".format(i, line))
            else:
                logger.debug("{0:03} {1}".format(i, line))
            i = i + 1
        logger.info("running...")

    def _report_rowcount(self, execution_time):
        if self.cursor.rowcount >= 0:
            logger.info("Completed in {0}s. {1} rows affected\n".format(
                execution_time.seconds,
                self.cursor.rowcount))
        else:
            logger.info("Completed in {0}s\n".format(execution_time.seconds))

    def _get_queries(self, query_file, parameters, replace):

        if query_file[-4:] == ".sql":
            if os.path.isfile(query_file):
                logger.info("Loading query from {0}".format(query_file))
                f = open(query_file, "r")
                text = f.read()
                f.close()
            else:
                logger.error("File {0} does not exist".format(query_file))
                raise OSError("File {0} does not exist".format(query_file))
        else:
            text = query_file

        for key in replace:
            text = text.replace(key, replace[key])

        # split into multiple commands....
        return self._prepare_sql(text, parameters)

    def _run_and_log_sql(self, command, parameters, pandas=False):
        sql = command.strip()
        df = None
        if sql != '':
            self._print_query(sql, parameters)
            start_time = datetime.datetime.now()
            if pandas:
                df = pd.io.sql.read_sql(sql,
                                        self.connection,
                                        params=parameters)
            else:
                self.cursor.execute(sql, parameters)
            self._report_rowcount(datetime.datetime.now() - start_time)

        return df

    def execute_query(self, query, parameters={}, replace={}, first_to_run=1):
        """
        Runs a query and ignores any output

        Parameters:
        - query - the query to run, either a SQL file or a SQL query
        - parameters - a dict of parameters to substitute in the query
        - replace - a dict or items to be replaced in the SQL text
        - first_to_run - the index of the first query in a mult-command query to be executed

        """

        i = 1
        for command in self._get_queries(query, parameters, replace):
            if i >= first_to_run:
                logger.info("RUNNING STATEMENT {0}...".format(i))
                self._run_and_log_sql(command=command,
                                      parameters=parameters,
                                      pandas=False)
            i = i + 1

        self.connection.commit()

    def execute_query_to_df(self, query, parameters={}, replace={}):
        """
        Runs a query and returns the output of the final statement in a DataFrame.

        Parameters:
        - query - the query to run, either a SQL file or a SQL query
        - parameters - a dict of parameters to substitute in the query
        - replace - a dict or items to be replaced in the SQL text

        """

        commands = self._get_queries(query, parameters, replace)

        # grab the final command as the select...
        select_command = commands.pop().strip()
        # last command may be blank if there's a trailing semicolon....
        if select_command == '':
            select_command = commands.pop().strip()

        for command in commands:
            self._run_and_log_sql(command=command,
                                  parameters=parameters,
                                  pandas=False)

        # now run the select
        df = self._run_and_log_sql(command=select_command,
                                   parameters=parameters,
                                   pandas=True)

        if len(df) == 0:
            logger.info("No results returned")
            return pd.DataFrame()
        else:
            return df

    def execute_query_to_csv(self, query, csvfile, parameters={}, replace={}, append=False):
        """
        Runs a query and writes the output of the final statement to a CSV file.

        Parameters:
        - query - the query to run, either a SQL file or a SQL query
        - csvfile - the file name to save the query results to
        - parameters - a dict of parameters to substitute in the query
        - replace - a dict or items to be replaced in the SQL text

        """

        commands = self._get_queries(query, parameters, replace)

        # run each command in turn
        for command in commands:
            self._run_and_log_sql(command=command,
                                  parameters=parameters,
                                  pandas=False)

        # delete an existing file if we are not appending
        if os.path.exists(csvfile) and append:
            file_mode = 'a'
        else:
            file_mode = 'w'

        # now get the data
        with open(csvfile, file_mode) as f:
            writer = csv.writer(f, delimiter=',')

            # write the header if we are writing to the beginning of the file
            if file_mode == 'w':
                writer.writerow([desc[0] for desc in self.cursor.description])

            for row in self.cursor:
                writer.writerow(row)
