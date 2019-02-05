import logging
import re
import string
import copy
import datetime
# parse xml file
def recursive_navigate(node, paths, index):
    try:
        r = node
        for result in node.findall(paths[index]):
            if (index < len(paths) - 1):
                return recursive_navigate(result, paths, index + 1)
            else:
                return result
        return None
    except Exception as e:
        logging.error("Error. " + str(e))
        return None


# extract all values from single node
def extract_all_items_from_node(node, name):
    try:
        return node.findall(name)

    except Exception as e:
        logging.error("Error. " + str(e))


# check exists node in multiple paths
def check_exists_node(node, paths):
    try:
        result_node = None

        for path in paths:
            result_node = recursive_navigate(node, path, 0)
            if result_node != None:
                break

        return result_node
        pass
    except Exception as e:
        logging.error("Error. " + str(e))
        return None


def convert_str():
    try:

        pass
    except Exception as e:
        pass

# convert output values
def convert_output_values(formats, values):
    try:

        output_values = []
        _value  =''
        for value in values:
            _value = copy.copy(value)

            for f in formats:
                index =0

                #only numbers
                if (f.value == 1):
                    if (_value == ''):

                        _value = '0'
                    # convert to float
                    _value = float(re.sub('[^0-9.]', "", _value.replace(",", ".")))

                #date
                if (f.value==2):
                    pass
                    # if (_value!=''):
                    #     lst = str(_value).split(' ')
                    #
                    #     if (len(lst)>0):
                    #         s_date = lst[0]
                    #         if (s_date!=''):
                    #             date = datetime.datetime.strptime(s_date,'dd.mm.yyyy')


                #thousand div
                if (f.value == 3):
                    if (_value == ''):
                        _value = 0
                    _value = round(_value / 1000, 2)

                index+=1


            output_values.append(_value)



        pass

        t = 0
        return output_values
    except Exception as e:
        logging.error("Error. " + str(e))
        return values


# extracted value join
def extract_value_join(column, values):
    try:
        value = ''
        if (column.extract_value_type.value == 0):
            for v in values:
                value += str(v)

            pass
        elif (column.extract_value_type.value == 1):
            index = 0
            for v in values:
                value += str(v)
                if (index < len(values) - 1):
                    value += ' '
                index += 1

            pass
        elif (column.extract_value_type.value == 2):
            index = 0
            for v in values:
                value += str(v)
                if (index < len(values) - 1):
                    value += '\n'
                index += 1

        # for value in values:

        return value
        pass
    except Exception as e:
        logging.error("Error. " + str(e))
        return None


# extract value from field non table content
def extract_data_from_extra_table_field(root, column):
    try:
        # проверяем пути в в основной секции, если они есть
        column_paths = column.value_paths
        value_attribute_name = column.value_attribute_name
        if (column_paths != None and len(column_paths) > 0):

            paths_to_values = []
            # путь основной, если в массиве только один элемент
            if (len(column_paths) == 1):
                paths_to_values = column_paths[0]
            else:
                # иначе необходимо проверить наличие первой попавшейс секции

                for column_path in column_paths:
                    result_path = check_exists_node(root, column_path)
                    if (result_path != None):
                        paths_to_values = column_path
                        break

            values = []
            # вытягиваем значения и записываем их в словарь
            for path_value in paths_to_values:
                node_value = recursive_navigate(root, path_value, 0)

                if (node_value != None):
                    value = node_value.get(value_attribute_name)

                    if (value != None):
                        values.append(value)

            extracted_value = extract_value_join(column, values)

            # здесь еще возможны алгоритмы преобразования конвертации и т.д.


            return extracted_value

        else:
            # если путей в столбце нет
            pass

        return ""

        pass
    except Exception as e:
        logging.error("Error. " + str(e))
        return ""


# extract value from xml table
def extract_data_from_table_row(xml_row, column):
    try:
        extracted_value = ''
        # проверяем пути в в основной секции, если они есть
        column_paths = column.value_paths
        value_attribute_name = column.value_attribute_name
        if (column_paths != None and len(column_paths) > 0):

            paths_to_values = []
            # путь основной, если в массиве только один элемент
            if (len(column_paths) == 1):
                paths_to_values = column_paths[0]
            else:
                # иначе необходимо проверить наличие первой попавшейс секции

                for column_path in column_paths:
                    result_path = check_exists_node(xml_row, column_path)
                    if (result_path != None):
                        paths_to_values = column_path
                        break

            values = []
            # вытягиваем значения и записываем их в словарь
            for path_value in paths_to_values:

                if (column.condition.is_multiple_values == False):
                    node_value = recursive_navigate(xml_row, path_value, 0)

                    if (node_value != None):
                        value = node_value.get(value_attribute_name)

                        if (value != None):
                            values.append(value)

                else:
                    node_values = extract_all_items_from_node(xml_row, path_value[0])

                    for node_value in node_values:
                        if (node_value != None):
                            value = node_value.get(value_attribute_name)

                            if (value != None):
                                values.append(value)

            if (column.condition.output_value_formats != None and len(column.condition.output_value_formats) > 0):
                values =convert_output_values(column.condition.output_value_formats, values)
                pass

            # convertation if needed
            extracted_value = extract_value_join(column, values)

        return extracted_value
        pass
    except Exception as e:
        logging.error("Error. " + str(e))
        return ""
