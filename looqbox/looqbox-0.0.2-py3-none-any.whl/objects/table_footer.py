from looqbox.objects.looq_object import LooqObject
import pandas as pd
from collections import defaultdict, OrderedDict
import types

class TableFooter(LooqObject):

    def __init__(self, table_data=None, total=None, total_link=None, total_style=None, total_tooltip=None,
                 value_format=None):
        super().__init__()
        self.table_data = table_data
        self.total = total
        self.total_link = total_link
        self.total_style = total_style
        self.total_tooltip = total_tooltip
        self.value_format = value_format

    @staticmethod
    def _get_elements_attributes(col_name, col_attribute):
        element_attribute = None

        if col_attribute is not None and col_name in col_attribute.keys():
            # If function call the function with the col_name
            if isinstance(col_attribute, types.FunctionType):
                element_attribute = col_attribute(col_name)
            else:
                element_attribute = col_attribute[col_name]

        return element_attribute

    @staticmethod
    def _transform_droplist(data_drop):

        link_list = []

        for col in data_drop:
            if 'text' in data_drop[col].keys() and len(data_drop[col]['text'].strip()) > 0:
                text = data_drop[col]['text']

                if 'link' in data_drop[col].keys() and len(data_drop[col]['link'].strip()) > 0:
                    link = data_drop[col]['link']
                    link_list.append({"text": text, "link": link})

        return link_list

    @staticmethod
    def _format_to_class(value_format):

        value_format = value_format.split(":")

        s = value_format[0].strip()

        return "lq" + s[0:1].upper() + s[1:]

    @property
    def to_json_structure(self):

        table_total = self.total
        table_data = self.table_data
        if isinstance(self.table_data, pd.DataFrame):
            table_data = table_data.to_dict(into=OrderedDict, orient='dict')

        total_dict = OrderedDict()
        if isinstance(table_total, list):

            if len(table_total) != len(table_data.keys()):
                raise Exception('"Total" size is different from the number of columns. To use total this way, '
                                'please use a dictionary.')

            table_total_index = 0
            for key in table_data.keys():
                total_dict[key] = table_total[table_total_index]
                table_total_index += 1

        elif isinstance(table_total, dict):
            table_total_index = 0
            for key in table_data.keys():
                if key in table_total.keys():
                    total_dict[key] = table_total[key]
                else:
                    total_dict[key] = "-"
                table_total_index += 1

        footer_list = []
        for col_name in total_dict:

            # Get columns attributes
            value_style = self._get_elements_attributes(col_name, self.total_style)
            value_link = self._get_elements_attributes(col_name, self.total_link)
            value_format = self._get_elements_attributes(col_name, self.value_format)

            value_tooltip = None
            if self.total_tooltip is not None and col_name in self.total_tooltip.keys():
                if isinstance(self.total_tooltip, dict):
                    value_tooltip = self.total_tooltip[col_name]
                else:
                    value_tooltip = self.total_tooltip

            # Initializing a dict with keys: None
            element = {'value': None, 'style': None, 'link': None, 'tooltip': None, 'format': None, 'class': None}

            value = total_dict[col_name]

            # Add value to the dict
            if isinstance(value, LooqObject):
                element['value'] = value.to_json_structure
            else:
                element['value'] = value

            # Add style to the dict
            if value_style is not None:
                if isinstance(value_style, types.FunctionType):
                    element['style'] = value_style(value)

                elif isinstance(value_style, pd.DataFrame):
                    element['style'] = value_style[col_name]

                else:
                    element['style'] = value_style

            # Add link to the dict
            if value_link is not None:
                if isinstance(value_link, types.FunctionType):
                    element['link'] = value_link(value)

                elif isinstance(value_link, dict):
                    # If the dict will contain a key droplist, the key link should not exist
                    del element['link']
                    element['droplist'] = self._transform_droplist(value_link)

                elif isinstance(value_link, str):
                    element['link'] = value_link

                else:
                    raise Exception("Formato de link não permitido")

            # Add tooltip to the dict
            if value_tooltip is not None:
                if len(value_tooltip.strip()) != 0:
                    element['tooltip'] = value_tooltip

            # Add format to the dict
            elif value_format is not None:
                if isinstance(value_format, types.FunctionType):
                    element['format'] = value_format(value)
                    element['class'] = self._format_to_class(value_format)

                elif isinstance(value_format, pd.DataFrame):
                    element['format'] = value_format[col_name]
                    element['class'] = self._format_to_class(value_format[col_name])

                else:
                    element['format'] = value_format
                    element['class'] = self._format_to_class(value_format)

                # Add the element dict to the value cell
            element = self.remove_json_nones(element)
            footer_list.append(element)

        # Create general json
        footer_json = {"content": footer_list}

        return footer_json


