# this script create a sqlite database from an excel file
import os
import sqlite3
import pandas as pd


def _load_price_data(filename_xlsx):
    """
    This function loads the Excel file which contain the data about the price.
    :param filename_xlsx: the excel file with the price data
    :return: A ordered dict of DataFrame with the price data. One dataframe by technology.
             + A dict with the technology as keys and the units as values.
    """

    data_price = pd.read_excel(filename_xlsx, sheet_name=None)
    units = data_price[list(data_price.keys())[0]]
    del data_price[list(data_price.keys())[0]]
    list_techno = list(data_price.keys())

    return data_price, list_techno, units


def create_database(filename_xlsx, database_name="price_database.db", erase_old=True):
    """
    This function transfer the xlsx file to a sqlite database. It erase old databases if erase is True.
    The data is contained in an excel file with one sheet by technology. Each line in the sheet is one price data with
    the following info: units, cost_machine, cost_installation, CAPEX, maintenance, reference, note. All data optional
    apart from units. Careful about the escape character in the raw data used to fill the database ,(,),*

    :param filename_xlsx: the excel file with the price data format as indicated above.
    :param database_name: the name of the database
    :param erase_old: If True, erase the old database with the same name
    """

    # column name and parameter
    name_col = ['myind', 'units', 'cost_machine', 'cost_installation', 'CAPEX', 'maintenance', 'reference', 'note']
    name_unittable = 'UNIT_TECHNO'
    name_colunit = ['techno', 'units']

    # format column name for sql
    col_table = '{} INTEGER PRIMARY KEY, {} FLOAT, {} FLOAT, {} FLOAT, {} FLOAT, {} FLOAT, {} TEXT, {} TEXT'\
                .format(*tuple(name_col))
    col_unittable = '{} TEXT PRIMARY KEY, {} TEXT'.format(*tuple(name_colunit))

    # erase old database if needed
    if erase_old and os.path.isfile(database_name):
        os.remove(database_name)

    # load the excel files
    data_price, list_techno, units = _load_price_data(filename_xlsx)

    # create database and cursor
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    # create table with the unit and fill it
    cursor.execute("CREATE TABLE {}({})".format(name_unittable, col_unittable))  # why ? do not work
    conn.commit()
    request_load = "INSERT INTO {}({}) values(?,?)".format(name_unittable, ', '.join(name_colunit))
    for u in units.values:
        cursor.execute(request_load, (u[0], u[1]))
        conn.commit()

    # create table with price data
    for t in list_techno:

        # create the table
        cursor.execute("CREATE TABLE {}({})".format(t, col_table))
        conn.commit()
        # insert the data line by line
        request_load = "INSERT INTO {}({}) values(?,?,?,?,?,?,?,?)".format(t, ', '.join(name_col))
        for i, row in enumerate(data_price[t].values):
            row[pd.isnull(row)] = 'NULL'
            cursor.execute(request_load, (i, ) + tuple(row))
            conn.commit()

    # close database
    conn.close()


def main():

    filename_xlsx = r'price_data_to_create_sqldatabase.xlsx'
    create_database(filename_xlsx)


if __name__ == '__main__':
    main()