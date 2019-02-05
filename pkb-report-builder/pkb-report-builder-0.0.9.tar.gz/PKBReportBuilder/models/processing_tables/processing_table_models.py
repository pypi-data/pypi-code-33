import logging
from enum import Enum


# collection of value data types
class ValueDataTypesCollection(Enum):
    SIMPLE_VALUE = 0
    GROUP_VALUE = 1
    ARRAY_VALUE = 2
    CONDITION_VALUE = 3


# convert types collection
class ConvertTypesCollection(Enum):
    WITHOUT = 0
    ONLY_NUMBERS = 1
    DATE = 1


# CONDITION TYPES
class ConditionTypesCollection():
    EQUAL = 0
    NOT_EQUAL = 1
    MORE_THAN = 2
    LESS_THAN = 3
    EXISTS = 4


# OUTPUT|EXTRACTED FORMAT
class OutputValueTypesCollection(Enum):
    WITHOUT = 0
    ONLY_NUMBERS = 1
    DATE = 2
    MONEY_FORMAT = 3
    THOUSAND_FORMAT = 4


# extract value types
class ExtractValueTypesCollection(Enum):
    SINGLE = 0
    JOIN_VALUE = 1
    JOIN_LIST = 2


# condition value
class ConditionValue():
    # constructor
    def __init__(self,
                 # path to xml condition block
                 path_to_condition,
                 # condition value attribute path value in xml block
                 value_for_check_condition_attribute,
                 # path to extracted value
                 path_to_value,
                 # attribute for extracted path value in xml block
                 value_attribute,
                 # ConvertTypesCollection for condition value
                 convert_value_for_checking_type,
                 # ConvertTypesCollection for extract value
                 convert_value_type,
                 # ConditionTypesCollection
                 condition_logic,
                 # condition equal values array
                 condition_equal_values,
                 #output value formats
                 output_value_formats,
                 # is mulitple value or single
                 is_multiple_values=False):
        try:

            self.path_to_condition = path_to_condition
            self.value_for_check_condition_attribute = value_for_check_condition_attribute
            self.path_to_value = path_to_value
            self.value_attribute = value_attribute,
            self.convert_value_for_checking_type = convert_value_for_checking_type
            self.convert_value_type = convert_value_type
            self.condition_logic = condition_logic
            self.condition_equal_values = condition_equal_values
            self.output_value_formats =output_value_formats
            self.is_multiple_values = is_multiple_values

        except Exception as e:
            logging.error("Error initialization. " + str(e))


# processing table cells
class ProcessingTableCell():
    # constructor
    def __init__(self, column):
        try:
            self.value = ""
            self.column = column
            self.index = column.index
        except Exception as e:
            logging.error("Error initialization. " + str(e))

    # convert value
    def convert_value(self, value):
        try:
            return value
        except Exception as e:
            logging.error("Error convert cell value. " + str(e))

    # set value
    def set_value(self, value):
        try:
            if (self.column.output_value_type.value != 1):
                self.value = self.convert_value(value)
            else:
                self.value = value
        except Exception as e:
            logging.error("Error set value to cell. " + str(e))


# processing table row
class ProcessingTableRow():
    # constructor
    def __init__(self, index, columns):
        try:
            self.index = index
            self.columns = columns
            self.cells = []
            self.is_root = False
            self.group_id =-1
            self.not_classificated =False
        except Exception as e:
            logging.error("Error initialization. " + str(e))

    # self init row cells by column params
    def init_cells_by_columns(self):
        try:
            for column in self.columns:
                self.cells.append(ProcessingTableCell(column))
        except Exception as e:
            logging.error("Error initialization. " + str(e))

    #set cell value by index
    def set_cell_value_by_index(self,index,value):
        try:
            for cell in self.cells:
                if (cell.column.index==index):
                    cell.value = value
                    return
        except Exception as e:
            logging.error("Error initialization. " + str(e))

    #set cells styles
    def set_cells_styles(self,style):
        try:

            pass
        except Exception as e:
            logging.error("Error initialization. " + str(e))

# processing table header
class ProcessingTableColumn():
    # constructor
    def __init__(self, index, title, name, value_paths, value_attribute_name, condition, extract_value_type,
                 extra_table_field=False):
        try:
            self.title = title
            self.name = name
            self.index = index
            self.value_paths = value_paths
            self.value_attribute_name = value_attribute_name
            self.extract_value_type = extract_value_type
            self.condition = condition
            self.extra_table_field = extra_table_field
        except Exception as e:
            logging.error("Error initialization. " + str(e))


# class processing table, for complex analyse
class ProcessingTable():
    # constructor
    def __init__(self, title, root_path, table_path, show_title=True,hidden_columns_in_groups=[]):
        try:
            self.title = title
            self.show_title = show_title
            self.table_path = table_path
            self.root_path = root_path
            self.columns = []
            self.rows = []
            self.group_rows = []
            self.hidden_columns_in_groups = hidden_columns_in_groups
        except Exception as e:
            logging.error("Error initialization. " + str(e))

    # init single column
    def init_column(self, title, name, value_paths, value_attribute_name, condition, extract_value_type,
                    extra_table_field=False):
        try:
            column_index = len(self.columns) + 1
            column = ProcessingTableColumn(column_index, title, name, value_paths, value_attribute_name, condition,
                                           extract_value_type, extra_table_field)
            self.columns.append(column)

        except Exception as e:
            logging.error("Error initialization. " + str(e))

    # def group rows by column values
    def group_rows_by_values(self, column):
        try:
            pass
        except Exception as e:
            logging.error("Error initialization. " + str(e))

    # init table row
    def init_row(self, index, columns):
        try:
            row = ProcessingTableRow(index, columns)
            row.init_cells_by_columns()
            self.rows.append(row)

            return self.rows[len(self.rows) - 1]
        except Exception as e:
            logging.error("Error initialization. " + str(e))
