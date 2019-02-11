# coding: utf-8
import json
import enum
import re


def build_all_of_type_queries(count_nodes,
                              gql_type=None,
                              query_str=None,
                              limit=None,
                              query_filter=None,
                              batch_size=50,
                              offset=0):
    """
    Arguments
        query_filter: filter on the gql_type. e.g. id_not :
            "sdflæjonsdfkæjgnsdæfkj". Parenthesis and 'filter' keywords
            should not be included in query_filter
        offset: start from record number offset
    """
    if limit:
        number_of_nodes = limit
    else:
        number_of_nodes = count_nodes

    all_type_key = _get_all_type_key(gql_type)
    query_cleaned = cleanup_query(query_str)

    if limit is not None:
        if limit < batch_size:
            batch_size = limit

    number_of_batches = number_of_nodes // batch_size
    last_batch_size = number_of_nodes % batch_size
    if last_batch_size > 0:
        number_of_batches += 1

    if number_of_batches == 1:
        last_batch_size = batch_size

    list_of_query_strings = []
    for batch in range(number_of_batches):

        first = batch_size
        if batch == number_of_batches - 1:  # last batch
            first = last_batch_size
        skip = batch * batch_size

        batch_key = 'p{}_{}'.format(str(skip),
                                    str(skip + first))
        all_type_query = '{{{}:{}(first: {} skip: {}'.format(batch_key,
                                                             all_type_key,
                                                             first,
                                                             skip)
        if query_filter is not None:
            all_type_query += ', where : {{ {} }} '.format(query_filter)
        all_type_query += '){{ {} }},'.format(query_cleaned)
        all_type_query += '}'
        list_of_query_strings.append(all_type_query)

    return list_of_query_strings


def _get_all_type_key(gql_type: str) -> str:
    if gql_type.endswith('s'):
        all_type_key = '{}es'.format(gql_type)
    elif gql_type.endswith('y'):
        all_type_key = '{}ies'.format(gql_type[:-1])
    else:
        all_type_key = '{}s'.format(gql_type)

    return all_type_key


def build_update_mutations(data,
                           gql_type=None,
                           returned_fields=['id'],
                           batch_size=20):
    """Update mutation

    Arguments:
        data:   dict of dicts. keys in top level dict holds graphcool ids.
                child dict hold key valuepairs of fields that are to be updated
    """
    if type(data) is not dict:
        raise Exception('fields_values is not a dict -- exiting')
    update_counter = 0
    node_count = len(data.keys())
    query_string = ''
    update_string = ''
    list_of_mutation_strings = []

    for id, node in data.items():
        update_string += '''{} :update{} ('''.format(id, gql_type)
        for key, value in node.items():
            update_string += """{} : """.format(key)
            if type(value) is str or value is None:
                value_escaped = value.replace('"', '\\\"')
                update_string += '''"{}",'''.format(value_escaped)
            elif type(value) is list:
                update_string += '{}, '.format(json_to_graphql(value))
            elif type(value) is dict:
                update_string += '"{}, "'.format(json_to_graphql(value).replace('"', '\\\"'))
            elif isinstance(value, enum.Enum):
                update_string += '{}, '.format(value.name)
            else:
                print(value)
                raise Exception('values must be strings -- exiting')
        update_string += """){"""
        update_string += """,""".join(returned_fields)
        update_string += """} ,"""
        update_counter += 1
        if update_counter % batch_size == 0 or update_counter >= node_count:
            query_string = 'mutation {'
            query_string += update_string
            query_string += '}'
            list_of_mutation_strings.append(query_string)
            update_string = ''
            query_string = ''

    return list_of_mutation_strings


def build_delete_nodes_mutations(node_ids: list, gql_type: str, batch_size=200):
    list_of_mutation_strings = []
    delete_nodes_query_str = ''
    gql_type_first_letter_uppercase = gql_type[0].upper() + gql_type[1:]
    for count_ids, node_id in enumerate(node_ids):
        delete_nodes_query_str += '''{} :delete{} ('''.format(node_id, gql_type_first_letter_uppercase)
        delete_nodes_query_str += """id : "{}" )  {{ id }},""".format(node_id)

        if count_ids + 1 % batch_size == 0 or count_ids + 1 >= len(node_ids):
            query_string = 'mutation {'
            query_string += delete_nodes_query_str
            query_string += '}'
            list_of_mutation_strings.append(query_string)
            delete_nodes_query_str = ''

    return list_of_mutation_strings


def cleanup_query(query):
    query = query.replace(" ", "")
    query = query.replace("""{\n""", "{")
    query = query.replace("\n", ",")
    query = query.replace("\\n", ",")

    return query


def json_to_graphql(query_dict: dict) -> str:
    json_str = json.dumps(query_dict)
    # search for:  "key": "value"
    key_with_quotation_marks_regex = r'(?:\":?)(\w+)(?:\":?)(?=\s*:)'
    key_with_quotation_marks_search_results = re.findall(key_with_quotation_marks_regex, json_str)
    if key_with_quotation_marks_search_results:
        for key_str_inside_quotation_marks in key_with_quotation_marks_search_results:
            json_str = json_str.replace(f'"{key_str_inside_quotation_marks}"', key_str_inside_quotation_marks)

    return json_str
