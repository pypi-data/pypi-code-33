from collections import OrderedDict
from looqbox.objects.looq_table import ObjTable
from looqbox.view.response_frame import ResponseFrame
from looqbox.global_calling import GlobalCalling
from looqbox.integration.looqbox_global import Looqbox
import pandas as pd
import re

__all__ = ["data_comp", "transpose_data", "find_token"]

# Calling global variable
GlobalCalling.set_looq_attributes(Looqbox())

def find_token(text, token_head, token_type="string"):
    """
    Find a token from a text using a token_head as base

    :param text: Text where the token is
    :param token_head: Base to be search in the text
    :param token_type: Type of the token, can be a string or a digit
    :return:
    """
    if token_type == "string":
        value_regex = ":? ?(\\S+)"
    elif token_type == "digit":
        value_regex = ":? ?(\\d+)"

    p = re.compile(token_head + value_regex)
    tokens = p.findall(text)

    return tokens


def data_comp(table1, table2, by=None, cols_to_compare=None):
    """
    Creates a ObjTable with values of comparision between table1 and table2.

    Example:
        table1 = ObjTable(data=pd.DataFrame({'Loja': ['SP', 'RJ'],
                                             'Vendas': [2500, 5300]}))
        table2 = ObjTable(data=pd.DataFrame({'Loja': ['SP', 'RJ'],
                                             'Vendas': [500, 1300]}))

        table = data_comp(table1, table2, by='Loja')

    :param table1: An ObjTable object
    :param table2: An ObjTable object
    :param by: Column(s) of type character shared between the two tables
    :param cols_to_compare: Columns to be compared
    :return: An ObjTable object that inherits the value_format of the table1 as well as the total type
    """
    if isinstance(table1, ResponseFrame):
        table1 = table1.content

    if isinstance(table2, ResponseFrame):
        table2 = table2.content

    if not isinstance(table1, ObjTable):
        raise Exception("First argument is not an ObjTable object")

    if not isinstance(table2, ObjTable):
        raise Exception("Second argument is not an ObjTable object")

    comparative_data = _comp_tables(table1, table2, by, cols_to_compare)

    delta_table = ObjTable()
    col_order = comparative_data.keys()
    delta_table.data = pd.DataFrame(comparative_data, columns=col_order)

    if table1.value_format is not None:
        _add_delta_format(delta_table, table1)

    if table1.total is not None:
        total_table1 = table1.total
        total_table2 = table2.total

        if not len(total_table1.keys()) == len(table1.data.keys()):
            raise Exception("Total size is different from number of cols")

        comparative_total = _comp_totals(total_table1, total_table2, by, cols_to_compare)
        delta_table.total = comparative_total

    return delta_table


def _add_delta_format(delta_table, table1):
    delta_table.value_format = {}
    for col in table1.value_format.keys():
        for delta_col in delta_table.data.keys():

            if "D_" in delta_col:
                delta_table.value_format[delta_col] = "percent:2"
            elif col in delta_col:
                delta_table.value_format[delta_col] = table1.value_format[col]


def _comp_tables(table1, table2, by=None, cols_to_compare=None):
    if isinstance(table1, ObjTable):
        d1 = table1.data.to_dict()
    else:
        d1 = table1

    if isinstance(table2, ObjTable):
        d2 = table2.data.to_dict()
    else:
        d2 = table2

    d3 = OrderedDict()

    # If by is None, get first column name
    if by is None:
        by = list(d1.keys())[0]

    # If cols_to_compare is None, use all the columns of the table
    if cols_to_compare is None:
        cols_to_compare = d1.keys()
    else:
        cols_to_compare = by + cols_to_compare

    for cols in cols_to_compare:
        try:
            if cols in by:
                d3[cols] = {rows: d1[cols][rows] for rows in d1[cols].keys()}
            elif cols in d1.keys() and cols in d2.keys():
                d3[cols + "_P1"] = {rows: d1[cols][rows] for rows in d1[cols].keys()}
                d3[cols + "_P2"] = {rows: d2[cols][rows] for rows in d2[cols].keys()}
                d3["D_" + cols] = {rows: (d1[cols][rows] / d2.get(cols, 0)[rows]) - 1 for rows in d1[cols].keys()}
        except TypeError:
            raise TypeError("Column " + cols + " is not a numeric type")
        except:
            raise Exception("Column " + cols + " not in both data frames")

    return d3


def _comp_totals(total1, total2, by=None, cols_to_compare=None):
    d3_total = OrderedDict()

    # If cols_to_compare is None, use all the columns of the table
    if cols_to_compare is None:
        cols_to_compare = total1.keys()
    else:
        cols_to_compare = by + cols_to_compare

    for cols in cols_to_compare:
        try:
            if cols in by:
                d3_total[cols] = total1[cols]
            elif cols in total1.keys() and cols in total2.keys():
                d3_total[cols + "_P1"] = total1[cols]
                d3_total[cols + "_P2"] = total2[cols]
                d3_total["D_" + cols] = (total1[cols] / total2.get(cols, 0)) - 1
        except TypeError:
            raise TypeError("Column " + cols + " is not a numeric type")
        except:
            raise Exception("Column " + cols + " not in both data frames")

    return d3_total


def _rename_duplicated_values(values_list):
    value_before = None
    counter = 1
    index = 0
    for value in values_list:
        if index != 0:
            if value == value_before:
                values_list[index] = value + "." + str(counter)
                counter += 1
            else:
                counter = 1

        value_before = value
        index += 1


def _get_attributes(transposed_table, table_object):
    row_to_col_dict = {transposed_table.data.loc[row][0]: row for row in transposed_table.data.index}
    if table_object.value_style is not None:
        for col in table_object.value_style.keys():
            if transposed_table.row_style is None:
                transposed_table.row_style = dict()

            col_to_row_in_transpose = row_to_col_dict[col]
            transposed_table.row_style[str(col_to_row_in_transpose)] = table_object.value_style[col]

    if table_object.value_format is not None:
        for col in table_object.value_format.keys():
            if transposed_table.row_format is None:
                transposed_table.row_format = dict()

            col_to_row_in_transpose = row_to_col_dict[col]
            transposed_table.row_format[str(col_to_row_in_transpose)] = table_object.value_format[col]

    if table_object.value_link is not None:
        for col in table_object.value_link.keys():
            if col_to_row_in_transpose is None:
                col_to_row_in_transpose = row_to_col_dict[col]

            transposed_table.row_link = dict()
            transposed_table.row_link[str(col_to_row_in_transpose)] = table_object.value_link[col]


def transpose_data(table_object, columns_name=None):
    """
    Transpose a data frame and transform it in a ObjTable. The main difference in this function is that the user
    can choose the name of the first row of the transposed table
    :param table_object: Table to be transposed
    :param columns_name: Name of the columns of the transposed table. If the parameter is None the names of the columns
    will be the first row of the data frame.
    :return: A transposed data frame as a ObjTable object
    """

    # converting all to a pandas object
    if isinstance(table_object, ObjTable):
        data = table_object.data
    elif isinstance(table_object, pd.DataFrame):
        data = table_object
    elif isinstance(table_object, dict):
        data = pd.DataFrame(table_object)

    # If the user didn't pass a first_row, get the first columns as name
    if columns_name is None:
        cols_name = data.keys()[0]
        row_values = data.keys()

        # Transposing data frame
        data = data.T

        # Inserting new columns
        data.insert(0, cols_name, list(row_values))

        # Get rows values
        first_row_values = data.loc[cols_name]

        # Changing all the columns to the value of the first line
        data.columns = list(first_row_values)

        # Removing the first line of the data frame
        data = data.drop(data.index[[0]])

        data = data.reset_index()
        del data['index']

    else:
        cols_name = columns_name[0]
        row_values = [columns_name[0]] + list(data.keys())
        data.insert(0, columns_name[0], [columns_name[1]] * len(data.index))

        # Transposing data frame
        data = data.T

        # Inserting new columns
        data.insert(0, cols_name, list(row_values))

        # Get rows values
        first_row_values = list(data.loc[row_values[0]])

        _rename_duplicated_values(first_row_values)

        # Changing all the columns to the value of the first line
        data.columns = list(first_row_values)

        # Removing the first line of the data frame
        data = data.drop(data.index[[0]])

        data = data.reset_index()
        del data['index']

    transposed_table = ObjTable(data)

    _get_attributes(transposed_table, table_object)

    return transposed_table
