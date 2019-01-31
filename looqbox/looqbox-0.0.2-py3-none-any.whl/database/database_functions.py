__all__ = ["looq_sql_in", "looq_sql_close", "looq_connect", "looq_sql_execute"]

import json
import os
import jaydebeapi
import datetime
import pandas as pd
from looqbox.objects.looq_table import ObjTable
from looqbox.utils.utils import base64_decode
from looqbox.global_calling import GlobalCalling


def looq_connect(conn_name, parameter_as_json=False):
    """
    Execute a connection in a database.

    :param conn_name: Name of the database
    :param parameter_as_json: Set if the parameters will be in JSON format or not
    :return: A Connection object
    """
    try:
        if isinstance(GlobalCalling.looq.connection_config, dict):
            file_connections = GlobalCalling.looq.connection_config
        else:
            file_connections = open(GlobalCalling.looq.connection_config)
            file_connections = json.load(file_connections)
    except FileNotFoundError:
        raise Exception("File connections.json not found")

    try:
        if not parameter_as_json:
            conn_par = GlobalCalling.looq.connection_config[conn_name]
        else:
            conn_par = file_connections[conn_name]
    except KeyError:
        raise Exception("Connection " + conn_name + " not found in the file " + GlobalCalling.looq.connection_file)

    conn_file_name, conn_file_extension = os.path.splitext(conn_par['driverFile'])

    old_driver_file_path = os.path.join(GlobalCalling.looq.jdbc_path + '/' + conn_file_name + conn_file_extension)
    new_driver_file_path = os.path.join(GlobalCalling.looq.jdbc_path + '/' + conn_file_name)

    if new_driver_file_path:
        driver_path = list()
        for file in os.listdir(new_driver_file_path):
            if not file.startswith('.') and '.jar' in file:
                driver_path.append(new_driver_file_path + '/' + file)
    elif old_driver_file_path:
        driver_path = old_driver_file_path

    conn = jaydebeapi.connect(conn_par['driver'], conn_par['connString'],
                              {'user': conn_par['user'], 'password': base64_decode(conn_par['pass'])},
                              driver_path[0])

    return conn


def looq_sql_execute(connection, query, replace_parameters=None, close_connection=True, show_query=False):
    """
    Function to execute a query inside the connection informed. The result of the query will be
    transformed into a ObjTable to be used inside the response.


    :param connection: Connection name or class
    :param query: Query to get the table
    :param replace_parameters: List of parameters to be used in the query. These parameters will replace the numbers
    with `` in the query.
        Example:
            replace_parameters = [par1, par2, par3, par4]
            query = "select * from bd where par1=`1` and par2=`2` and par3=`3` and par4=`4`

            In this case the values of `1`, `2`, `3`, `4` will be replaced by par1, par2, par3, par4 respectively (using
            the order of the list in replace_parameters).

    :param close_connection: Define if automatically closes the connection
    :param show_query: Print the query in the console
    :return: A TableObject with the data retrieved from the query
    """

    if replace_parameters is not None:
        query = _sql_replace_parameters(query, replace_parameters)

    test_mode = GlobalCalling.looq.test_mode

    if show_query and test_mode:
        print(query)

    start_time = datetime.datetime.now()

    query_dataframe = ObjTable()
    query_dataframe.data = _get_query_result(connection, query, close_connection)
    df_cols_and_rows = query_dataframe.data.shape
    query_dataframe.rows = df_cols_and_rows[0]
    query_dataframe.cols = df_cols_and_rows[1]

    if test_mode:
        total_sql_time = datetime.datetime.now() - start_time
        print("SQL fetch in...", total_sql_time.total_seconds(), "secs")

    if close_connection and not isinstance(connection, str):
        connection.close()

    return query_dataframe


def _get_query_result(connection, query, close_connection):
    """
    Function to get the table resulting from the query

    :param connection: Connection name or class
    :param query: Query to get the table
    :param close_connection: Define if automatically closes the connection
    :return: Return the data frame resulting from the query.
    """
    try:
        if isinstance(connection, str):
            connection = looq_connect(connection)

        conn_curs = connection.cursor()
        conn_curs.execute(query)
        col_names = [i[0] for i in conn_curs.description]
        query_df = pd.DataFrame(conn_curs.fetchall(), columns=col_names)

        looq_sql_close(conn_curs)

        return query_df
    except:
        if close_connection and not isinstance(connection, str):
            conn_curs.close()
            looq_sql_close(conn_curs)

        raise Exception("Error to connect in database")


def _sql_replace_parameters(query, replace_parameters):
    """
    This function get the query and replace all the values between backticks to the values in the replace_parameters
    list, the values are substituted using the order in replace parameters, for example, the `1` in the query will be
    substituted by the value replace_parameters[0] and so goes on.
    Example:
        query = "select * from database where x = `1` and z = `3` and y = `2`"
        replace_parameters = [30, 50, 60}

        returns = "select * from database where x = 30 and z = 60 and y = 50"

    :param query: Query to be changed
    :param replace_parameters: List that contains the values to be substitute
    :return: Query with the values changed
    """
    for replace in range(len(replace_parameters)):
        query = query.replace('`' + str((replace + 1)) + '`', '"' + str(replace_parameters[replace]) + '"')

    return query


def looq_sql_in(query=None, values_list=None):
    """
    Transform the list in values_list to be used inside a IN statement of the SQL.
    Example:
        values_list = [1,2,3,4,5]
        query = 'select * from database where' + looq_sql_in(" col in", values_list)

        "select * from database where col in (1, 2, 3, 4, 5)"


    :param query: Query header with the first part of the query
    :param values_list: list to be transformed as a IN format
    :return: query concatenated with values_list as a IN format
    """
    if values_list is None:
        return ""

    if not isinstance(values_list, list):
        values_list = [values_list]

    separated_list = str(values_list).replace('[', '(').replace(']', ')')

    if query is None:
        return separated_list
    else:
        return query + " " + separated_list


def looq_sql_between(query=None, values_list=None):
    """
    Transform the list in values_list to be used as a between statement of the SQL.
    Example:
        values_list = ['2018-01-01', '2018-02-02']
        query = 'select * from database where looq_sql_between(' date', date_int)'

        "select * from database where date between '2018-01-01' and '2018-02-02')"


    :param query: Query header with the first part of the query
    :param values_list: list to be used in a between statement
    :return: query concatenated with values_list as a between statement
    """
    if values_list is None:
        return ""

    if len(values_list) != 2:
        raise Exception("To use looq_sql_between values_list must be of two positions")

    if not isinstance(values_list, list):
        values_list = [values_list]

    if isinstance(values_list[0], int) or isinstance(values_list[1], int):
        between_query = query + " between " + str(values_list[0]) + " and " + str(values_list[1])
    else:
        between_query = query + " between '" + values_list[0] + "' and '" + values_list[1] + "'"

    return between_query


def looq_sql_close(conn):
    """
    Close a connection
    :param conn: Connection of the type JayBeDeApi
    """
    conn.close()
