from looqbox.objects.looq_object import LooqObject
from looqbox.objects.table_cell import TableCell
from collections import defaultdict, OrderedDict
import pandas as pd
import json
import types


class TableBody(LooqObject):

    def __init__(self, data=None, value_format=None, value_style=None, col_tooltip=None, value_link=None, col_range=None,
                 row_style=None, row_format=None, row_link=None, row_tooltip=None, row_range=None):
        super().__init__()
        self.data = data
        self.value_format = value_format
        self.value_link = value_link
        self.value_style = value_style
        self.col_tooltip = col_tooltip
        self.col_range = col_range
        self.row_format = row_format
        self.row_link = row_link
        self.row_style = row_style
        self.row_tooltip = row_tooltip
        self.row_range = row_range

    @staticmethod
    def _get_col_attribute(col_name, col_attribute):
        """
        Return the attribute for a col_name.

        :param col_name: Name of the actual column that will be used to get it's respective attribute. [str]
        :param col_attribute: List or dictionary with all the attributes to each column. [list, dict]
        :return The attribute value of that col_name's attribute
        """

        attribute = None

        if col_attribute is not None and col_name in col_attribute:
            attribute = col_attribute[col_name]

        return attribute

    @staticmethod
    def _get_row_attribute(row_number, row_attribute):
        """
        Return the attribute for a row. But the preference of the attributes is for the column attributes.

        :param row_number: Number of the actual column that will be used to get it's respective attribute. [str]
        :param row_attribute: List or dictionary with all the attributes to each row. [list, dict]
        :return The attribute value of that row's attribute
        """

        attribute = None

        if row_attribute is not None and str(row_number) in row_attribute:
            attribute = row_attribute[str(row_number)]

        return attribute

    @staticmethod
    def _transform_droplist(data_drop):
        """
        Create the droplists for the table elements

        :return List of dictionaries with keys text and link
        """

        link_list = []

        # If its a single dict it will be transformed into a list of dicts, however if its a str it will raise Exception
        if isinstance(data_drop, str):
            raise Exception("Links with only strings must not be in a list")

        if not isinstance(data_drop, list):
            data_drop = [data_drop]

        for link in data_drop:
            if isinstance(link, list):
                link = link[0]

            if 'text' not in link:
                raise Exception("Text missing in droplist link")
            elif 'link' not in link:
                raise Exception("Link missing in droplist link")

            for key, value in link.items():
                if key == 'text' and len(value.strip()) > 0:
                    text = value
                elif key == 'link' and len(value.strip()) > 0:
                    link = value

            link_list.append({"text": text, "link": link})

        return link_list

    @staticmethod
    def _format_to_class(value_format):
        """
        Converts a format to this class representation.

        :return format_class
        """

        if isinstance(value_format, list):
            format_class = []
            for format in value_format:
                format = format.split(":")

                s = format[0].strip()

                format_class.append("lq" + s[0:1].upper() + s[1:])
        else:
            value_format = value_format.split(":")

            s = value_format[0].strip()

            format_class = "lq" + s[0:1].upper() + s[1:]

        return format_class

    @staticmethod
    def create_row_dict(table_dict):
        """
        This function transform our dict based in columns to a dict based in rows.

        The interface reads and create the table based in rows, because of that the package needs to do this
        transformation.

        :return A list with dictionaries representing the rows of the table. The dictionary order is the same order of
            the table's rows
        """
        rows_by_index = defaultdict(list)

        # For each item in the table dict append in the row dict
        for column_name, column in table_dict.items():
            for index in range(len(column)):
                rows_by_index[index].append({column_name: column[index]})

        rows = defaultdict(list)
        for values in rows_by_index.values():
            for idx, line in enumerate(values):
                rows[idx].append(line)

        rows_dicts_list = []
        for key, elements in rows_by_index.items():
            temp_dict = defaultdict(list)
            for col_dict in range(len(rows_by_index[key])):
                if len(temp_dict) == 0:
                    temp_dict = rows_by_index[key][col_dict]
                else:
                    temp_dict.update(rows_by_index[key][col_dict])
            rows_dicts_list.append(temp_dict)

        return rows_dicts_list

    @staticmethod
    def get_cell_value(element, value):
        if isinstance(value, LooqObject):
            element.cell_value = json.loads(value.to_json_structure)
        else:
            element.cell_value = value

    @staticmethod
    def get_cell_style(element, row_index, value, value_style):
        if isinstance(value_style, types.FunctionType):
            element.cell_style = value_style(value)

        elif isinstance(value_style, pd.DataFrame):
            element.cell_style = value_style[row_index]

        elif isinstance(value_style, list):
            element.cell_style = value_style[row_index]

        else:
            element.cell_style = value_style

    def get_cell_link(self, element, value, value_link):
        if isinstance(value_link, types.FunctionType):
            element.cell_link = value_link(value)

        elif isinstance(value_link, list) or isinstance(value_link, dict):
            # If the dict will contain a key droplist, the key link should not exist
            element.cell_droplist = self._transform_droplist(value_link)

        elif isinstance(value_link, str):
            element.cell_link = value_link

        else:
            raise Exception("Link format not allowed")

    def get_cell_format(self, col_name, element, value, value_format):
        """
        Get the cell col format
        """
        if isinstance(value_format, types.FunctionType):
            element.cell_format = value_format(value)
            element.cell_class = self._format_to_class(value_format)

        elif isinstance(value_format, pd.DataFrame):
            element.cell_format = value_format[col_name]
            element.cell_class = self._format_to_class(value_format[col_name])

        else:
            element.cell_format = value_format
            element.cell_class = self._format_to_class(value_format)

    @staticmethod
    def get_cell_tooltip(element, value_tooltip):
        if len(value_tooltip.strip()) != 0:
            element.cell_tooltip = value_tooltip

    def get_rows_list(self, table_data):
        if self.row_range is None:
            self.row_range = [None, None]
        if self.row_range[0] is None:
            self.row_range[0] = 0
        if self.row_range[1] is None:
            self.row_range[1] = len(table_data)
        rows_list = list(range(0, len(table_data)))
        rows_list = rows_list[self.row_range[0]:self.row_range[1]]
        return rows_list

    @staticmethod
    def get_row_style(row_value_style, value):
        if isinstance(row_value_style, types.FunctionType):
            value.cell_style.update(row_value_style(value))
        # If value already has a style and the keys are not all equal
        elif value.cell_style is not None and value.cell_style.keys() != row_value_style.keys():
            # For each style key inside the row_value_style, I check if this key already exists inside my
            # actual value. If it already exists I ignore (column priority)
            for style_key in row_value_style:
                # Python points to the same address to all dicts. Because of this, the package are using
                # copy() to create a new style dict and after that changing the old one
                new_style = value.cell_style.copy()
                if style_key not in new_style:
                    new_style[style_key] = row_value_style[style_key]

                value.cell_style = new_style
        else:
            value.cell_style = row_value_style

    def get_row_link(self, row_value_link, value):
        if value.cell_link is not None:
            if isinstance(row_value_link, types.FunctionType):
                value.cell_link.update(row_value_link(value))

            elif isinstance(row_value_link, dict):
                # If the dict will contain a key droplist, the key link should not exist
                del value.cell_link
                value.cell_droplist.update(self._transform_droplist(row_value_link))

            elif isinstance(row_value_link, str):
                value.cell_link.update(row_value_link)

            else:
                raise Exception("Link format not allowed")
        else:
            if isinstance(row_value_link, types.FunctionType):
                value.cell_link = row_value_link(value.cell_link)

            elif isinstance(row_value_link, dict):
                # If the dict will contain a key droplist, the key link should not exist
                value.cell_droplist = self._transform_droplist(row_value_link)

            elif isinstance(row_value_link, str):
                value.cell_link = row_value_link

            else:
                raise Exception("Link format not allowed")

    @staticmethod
    def get_row_tooltip(row_value_tooltip, value):
        if value.cell_tooltip is None and len(row_value_tooltip.strip()) != 0:
            value.cell_tooltip = row_value_tooltip

    def get_row_format(self, row_value_format, value):
        if value.cell_format is None and value.cell_class is not None:
            if isinstance(row_value_format, types.FunctionType):
                value.cell_format = row_value_format(value)
                value.cell_class = self._format_to_class(row_value_format)

            else:
                value.cell_format = row_value_format
                value.cell_class = self._format_to_class(row_value_format)

    def _col_attributes_to_values(self, table_data):
        """
        Join the columns values with its attributes .


        :param table_data: General table body
        :return: The table with all the elements with the values
        """

        if self.col_range is None:
            self.col_range = [None, None]

        if self.row_range is None:
            self.row_range = [None, None]

        if self.col_range[0] is None:
            self.col_range[0] = 0

        if self.col_range[1] is None:
            self.col_range[1] = len(table_data.keys())

        if self.row_range[0] is None:
            self.row_range[0] = 0

        keys_list = list(table_data.keys())
        keys_list = keys_list[self.col_range[0]:self.col_range[1]]

        for col_name in table_data:

            rows_total_number = len(table_data[col_name].values())
            if self.row_range[1] is None:
                self.row_range[1] = rows_total_number

            rows_list = list(range(0, rows_total_number))
            rows_list = rows_list[self.row_range[0]:self.row_range[1]]

            col_in_range = True

            if col_name not in keys_list:
                col_in_range = False

            # Get columns attributes
            value_style = self._get_col_attribute(col_name, self.value_style)
            value_link = self._get_col_attribute(col_name, self.value_link)
            value_format = self._get_col_attribute(col_name, self.value_format)
            value_tooltip = None

            row_index = 0
            if self.col_tooltip is not None and col_name in self.col_tooltip.keys():
                if isinstance(self.col_tooltip, dict):
                    value_tooltip = self.col_tooltip[col_name]
                else:
                    value_tooltip = self.col_tooltip

            for value in table_data[col_name].values():

                row_in_range = True
                if row_index not in rows_list:
                    row_in_range = False

                element = TableCell()

                # Add value to the cell object
                self.get_cell_value(element, value)

                # Add style to the cell object
                if col_in_range and row_in_range and value_style is not None:
                    self.get_cell_style(element, row_index, value, value_style)

                # Add link to the cell object
                if col_in_range and row_in_range and value_link is not None:
                    self.get_cell_link(element, value, value_link)

                # Add tooltip to the cell object
                if col_in_range and row_in_range and value_tooltip is not None:
                    self.get_cell_tooltip(element, value_tooltip)

                # Add format to the cell object
                if col_in_range and row_in_range and value_format is not None:
                    self.get_cell_format(col_name, element, value, value_format)
                    if isinstance(element.cell_format, list) and len(element.cell_format) > row_index:
                        element.cell_format = element.cell_format[row_index]

                # Add the cell object to the value cell
                #  element = element.remove_json_nones(element.to_json_structure)
                table_data[col_name][row_index] = element
                row_index += 1

        return table_data

    def _row_attributes_to_values(self, table_data):
        """
        Join the columns values with its attributes .


        :param table_data: General table body
        :return: The table with all the elements with the values
        """

        rows_list = self.get_rows_list(table_data)

        for row_number in range(len(table_data)):

            row_in_range = True

            if row_number not in rows_list:
                row_in_range = False

            # Get columns attributes
            row_value_style = self._get_row_attribute(row_number, self.row_style)
            row_value_link = self._get_row_attribute(row_number, self.row_link)
            row_value_format = self._get_row_attribute(row_number, self.row_format)

            row_value_tooltip = None
            if self.row_tooltip is not None and str(row_number) in self.row_tooltip:
                if isinstance(self.row_tooltip, dict):
                    row_value_tooltip = self.row_tooltip[str(row_number)]
                else:
                    row_value_tooltip = self.row_tooltip

            for col in table_data[row_number]:

                value = table_data[row_number][col]

                # Add style to the dict
                if row_in_range and row_value_style is not None:
                    self.get_row_style(row_value_style, value)

                # Add link to the dict
                if row_in_range and row_value_link is not None:
                    self.get_row_link(row_value_link, value)

                # Add tooltip to the dict
                if row_in_range and row_value_tooltip is not None:
                    self.get_row_tooltip(row_value_tooltip, value)

                # Add format to the dict
                if row_in_range and row_value_format is not None:
                    self.get_row_format(row_value_format, value)

                # Add the element dict to the value cell
                table_data[row_number][col] = value

        return table_data

    @property
    def to_json_structure(self):
        """
        Generate the json that will be add in the ObjectTable body part.

        :return: body_json: Dictionary that will be converted to a JSON inside the looq_table function.

        """

        table_data = self.data
        if isinstance(table_data, pd.DataFrame):
            table_data = table_data.to_dict(into=OrderedDict, orient='dict')

        if table_data is None:
            return None

        # Reading all the values of the column to create the json for each one
        table_data = self._col_attributes_to_values(table_data)

        # Each position of the dict is a row
        table_data = self.create_row_dict(table_data)

        # Verifying rows attributes
        table_data = self._row_attributes_to_values(table_data)

        # Body general format
        body_format = list()
        if self.value_format is not None and self.col_range is None and self.row_range is None:
            body_format = self.value_format

        # Body general format classes
        body_class = list()
        if self.value_format is not None and self.col_range is None and self.row_range is None:
            for value_format in self.value_format.values():
                body_class.append(self._format_to_class(value_format))

        for row in table_data:
            for col in row.keys():
                row[col] = row[col].to_json_structure

        # Create general json
        body_json = {"content": table_data, "format": body_format, "class": body_class}

        return body_json
