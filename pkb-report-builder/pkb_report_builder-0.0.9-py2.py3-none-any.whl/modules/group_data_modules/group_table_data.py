import logging
import copy
import modules.table_processing.not_classificated_records as not_classificated_records
import models.root_models.root_model as root_model
import modules.root_processor.root_processor as root_processor


# check if value is root element in
def check_roots(values, value):
    try:
        if (value == ''):
            return False
        for _value in values:
            if (str(_value) != str(value) and str(_value).startswith(value)):
                return True

        return False
    except Exception as e:
        logging.error("Error. " + str(e))
        return False

        # check if value is root element in


def check_result_roots(values, value):
    try:

        for _value in values:
            if (_value != value and str(value).startswith(_value)):
                return False

        return True


    except Exception as e:
        logging.error("Error. " + str(e))
        return False


# get t contract roots
def get_to_roots(values):
    try:
        root_values = []
        for value in values:
            if (check_roots(values, value) == True):
                root_values.append(value)
        root_values.sort()
        # return root_values
        result_root_values = []
        for root_value in root_values:
            if (check_result_roots(root_values, root_value) == True):
                result_root_values.append(root_value)

        # #clean repea
        return result_root_values
    except Exception as e:
        logging.error("Error. " + str(e))
        return values


# get to single contracts without roots
def get_to_single_contracts(b_values, roots):
    try:
        for root in roots:
            for i in range(0, len(b_values)):
                if (str(b_values[i][0]) == str(root) or str(b_values[i][0]).startswith(str(root))):
                    b_values[i][1] = True

        single_roots = []
        for b_value in b_values:
            if (len(b_value) > 1):
                if (b_value[1] == False):
                    if (b_value[0] != ''):
                        single_roots.append(b_value[0])
        return single_roots
    except Exception as e:
        logging.error("Error. " + str(e))
        return []


# sum chid element
def sum_child_element(rows, group_id, column_id):
    try:
        result = 0
        founded = False
        for row in rows:
            if (row.is_root == False and row.group_id == group_id):
                value = float(row.cells[column_id].value)
                result += value
                founded = True

        if (founded == False):
            return None

        return round(result, 2)
    except Exception as e:
        logging.error("Error. " + str(e))
        return 0


# calculate child elements
def calculate_root_elements(table):
    try:
        column_names = ['TotalAmount', 'OutstandingAmount', 'MonthlyInstalmentAmount']
        for column_name in column_names:

            for row in table.rows:
                if (row.is_root == True):
                    column_index = -1
                    group_id = row.group_id
                    index = 0

                    for cell in row.cells:
                        if (cell.column.name == column_name):
                            column_index = index
                            break
                        index += 1
                    if (column_index == -1):
                        continue
                    sum_rows = sum_child_element(table.rows, group_id, column_index)
                    if (sum_rows != None):
                        row.cells[column_index].value = str(sum_rows)

        t = 0
    except Exception as e:
        logging.error("Error. " + str(e))


# get to table row by agreement number
def get_table_row_by_aggreement_number(table, cell_index, value):
    try:
        row_index = 0
        for row in table.rows:
            if (str(row.cells[cell_index].value) == str(value)):
                return row_index, row
        return -1, None
    except Exception as e:
        logging.error("Error. " + str(e))
        return -1, None


# group data by aggreement number
def group_data_table(table):
    try:
        # clean table
        # table, not_classificate_table = not_classificated_records.check_not_classificated_rows(table)


        column_name = 'AgreementNumber'
        values = []
        first_row = table.rows[0]
        cell_index = 0
        for cell in first_row.cells:
            if (cell.column.name == column_name):
                break
            cell_index += 1

        not_classificated_rows = []
        index = 0
        for row in table.rows:
            if (row.cells[cell_index].value != ''):
                values.append(row.cells[cell_index].value)
            else:
                not_classificated_rows.append(row)

        values.sort()

        sort_rows = []
        for value in values:
            for row in table.rows:
                if (str(row.cells[cell_index].value) == str(value)):
                    sort_rows.append(row)
                    continue

        root_models = []
        for value in values:
            root_models.append(root_model.RootModel(value))

        order_roots = root_processor.order_roots(root_models)

        table.rows = sort_rows

        sort_table = copy.deepcopy(table)
        sort_table.rows = []
        current_group_id = -1
        current_row_index = 1

        for order_root in order_roots:
            value = order_root[0]
            grouping = order_root[1]
            t = 0

            if (grouping == True):
                root_element = value[0]
                child_elements = value[1]

                current_group_id+=1
                # add root
                row_index, root_row = get_table_row_by_aggreement_number(table, cell_index,
                                                                         root_element.aggreement_value)
                start_row_group_index = current_row_index
                end_row_group_index = current_row_index
                root_row.is_root = True
                root_row.group_id = current_group_id
                sort_table.rows.append(root_row)
                current_row_index += 1

                # check childs if need add them
                for child_element in child_elements:
                    row_index, child_row = get_table_row_by_aggreement_number(table, cell_index,
                                                                              child_element.aggreement_value)

                    if (child_row != None):
                        child_row.group_id = current_group_id

                        # hidden_columns_in_groups
                        for cell in child_row.cells:
                            for hidden_column in table.hidden_columns_in_groups:
                                if (hidden_column == cell.column.name):
                                    cell.value = ''

                        sort_table.rows.append(child_row)
                        end_row_group_index+=1

                    current_row_index += 1

                if (start_row_group_index != -1 and end_row_group_index != -1):
                    if (start_row_group_index != end_row_group_index):
                        sort_table.group_rows.append([start_row_group_index, end_row_group_index])
                current_group_id += 1
            else:
                root_elements = []

                for v in value:
                    root_elements.append(v)

                for root_element in root_elements:
                    row_index, root_row = get_table_row_by_aggreement_number(table, cell_index,
                                                                             root_element.aggreement_value)

                    root_row.is_root = True
                    root_row.group_id = current_group_id
                    sort_table.rows.append(root_row)
                    current_row_index += 1




        calculate_root_elements(sort_table)

        table = copy.deepcopy(sort_table)

        for not_classificated_row in not_classificated_rows:
            not_classificated_row.not_classificated = True
            table.rows.append(not_classificated_row)

        return table
    except Exception as e:
        logging.error("Error. " + str(e))
