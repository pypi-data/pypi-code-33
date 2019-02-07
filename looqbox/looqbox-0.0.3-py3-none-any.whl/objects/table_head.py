from looqbox.objects.looq_object import LooqObject
import pandas as pd
from collections import OrderedDict
import types

class TableHead(LooqObject):

    def __init__(self, table_data=None, head_style=None, head_tooltip=None, head_group=None, head_group_tooltip=None,
                 show_head=None):

        super().__init__()
        self.table_data = table_data
        self.head_tooltip = head_tooltip
        self.head_style = head_style
        self.head_group = head_group
        self.head_group_tooltip = head_group_tooltip
        self.show_head = show_head

    def add_col_with_no_list(self, rows, values=None):

        if values is not None:
            values_list = values
        else:
            values_list = self.head_group

        group_index = 0
        for group in values_list:

            if group_index == 0:
                new_dict = {"value": group, "colspan": 1, "rowspan": 1}

            elif rows['cols'][group_index - 1]['value'] == group:
                rows['cols'][group_index - 1]['colspan'] += 1
                continue

            else:
                new_dict = {"value": group, "colspan": 1, "rowspan": 1}

            rows['cols'].append(new_dict)
            group_index += 1

    @staticmethod
    def add_list_col(rows, group_list):

        group_index = 0
        for group in group_list:

            if group_index == 0:
                new_dict = {"cols": []}
                new_dict['cols'].append({"value": group, "colspan": 1, "rowspan": 1})

            else:
                new_dict = {"cols": []}
                new_dict['cols'].append({"value": group, "colspan": 1, "rowspan": 1})

            rows.append(new_dict)
            group_index += 1

    def add_hybrid_col(self, rows):

        group_index = 0
        for group in self.head_group:

            if group_index == 0:
                if isinstance(group, list):
                    new_dict = {"cols": []}
                    self.add_col_with_no_list(new_dict)

                    rows.append(new_dict)
                    group_index += 1
                    continue

                else:
                    new_dict = {"cols": []}
                    new_dict['cols'].append({"value": group, "colspan": 1, "rowspan": 1})
            else:
                if isinstance(group, list):
                    new_dict = {"cols": []}
                    self.add_col_with_no_list(new_dict, group)

                    rows.append(new_dict)
                    group_index += 1
                    continue
                else:
                    new_dict = {"cols": []}
                    new_dict['cols'].append({"value": group, "colspan": 1, "rowspan": 1})

            rows.append(new_dict)
            group_index += 1

    def add_head_group(self):

        has_list = False
        rows = list()

        # Check the len to the possibility of a list of list
        # Vertically
        if self.head_group is not None and len(self.head_group) == 1:
            if isinstance(self.head_group[0], list):
                self.add_list_col(rows, self.head_group[0])

        elif self.head_group is not None:
            # Hybrid
            for head in self.head_group:
                if isinstance(head, list):
                    has_list = True

            # Horizontally
            if not has_list:
                rows = {"cols": []}
                self.add_col_with_no_list(rows)

            else:
                self.add_hybrid_col(rows)

        return rows

    @staticmethod
    def _get_elements_attributes(col_name, col_attribute):
        element_attribute = None

        if col_attribute is not None:
            # If function call the function with the col_name
            if isinstance(col_attribute, types.FunctionType):
                element_attribute = col_attribute(col_name)
            else:
                element_attribute = col_attribute[col_name]

        return element_attribute

    @property
    def to_json_structure(self):

        table_data = self.table_data
        if isinstance(table_data, pd.DataFrame):
            table_data = table_data.to_dict(into=OrderedDict, orient='dict')

        if table_data is None:
            return None

        head_list = list()
        for col_name in table_data:
            element = {'value': col_name,
                       'style': self._get_elements_attributes(col_name, self.head_style),
                       'tooltip': self._get_elements_attributes(col_name, self.head_tooltip)}

            element = self.remove_json_nones(element)

            head_list.append(element)

        if self.show_head is None:
            raise TypeError("Invalid type to the parameter show_head")

        if self.head_group is not None and len(self.head_group) == 0:
            return list()

        rows = self.add_head_group()

        if isinstance(rows, list):
            if len(rows) == 0:
                group_list = []
            else:
                group_list = {"rows": rows}
        else:
            group_list = {"rows": [rows]}

        header_json = {"content": head_list, "visible": self.show_head, "group": group_list}

        return header_json
