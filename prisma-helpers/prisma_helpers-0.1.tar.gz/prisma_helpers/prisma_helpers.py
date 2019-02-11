# coding: utf-8
"""document example of usage
"""

import asyncio
import json
import graphql_connection
import prisma_query_builders
import logging

logger = logging.getLogger(__name__)


async def all_of_type(graphql_connection_: graphql_connection.GraphQLConnection,
                      gql_type=None,
                      query_str=None,
                      limit=None,
                      query_filter=None,
                      batch_size=1000,
                      offset=0,
                      concurrent_tasks=50):
    if limit is None or limit > batch_size:
        count_nodes = await count_of_type(graphql_connection_, gql_type=gql_type, query_filter=query_filter)
    else:
        count_nodes = limit

    list_of_query_dicts = prisma_query_builders.build_all_of_type_queries(count_nodes,
                                                                          gql_type=gql_type,
                                                                          query_str=query_str,
                                                                          limit=limit,
                                                                          query_filter=query_filter,
                                                                          batch_size=batch_size,
                                                                          offset=offset)

    return await _submit_query(graphql_connection_, list_of_query_dicts, concurrent_tasks)


async def count_of_type(graphql_connection_, gql_type=None, query_filter=None):
    if gql_type.endswith('s'):
        all_type_key = '{}esConnection'.format(gql_type)
    elif gql_type.endswith('y'):
        all_type_key = '{}iesConnection'.format(gql_type[:-1])
    else:
        all_type_key = '{}sConnection'.format(gql_type)
    all_type_query = """ {{ {} """.format(all_type_key)
    if query_filter is not None:
        all_type_query += ' (where : {{ {} }})'.format(query_filter)
    all_type_query += """{ aggregate { count } } }"""

    number_of_nodes = await _submit_query(graphql_connection_, [all_type_query], 1, trim_query=False)

    if number_of_nodes is None:
        return 0
    else:
        try:
            return number_of_nodes[0]['aggregate']['count']
        except KeyError:
            print(number_of_nodes)
            raise Exception(
                'Oh no -- have a coffee -- something went wrong: ' + str(number_of_nodes))


async def _submit_query(graphql_connection_,
                        list_of_query_strings,
                        concurrent_tasks,
                        trim_query=False):
    if not list_of_query_strings:
        return []

    if trim_query:
        list_of_trimmed_query_strings = do_trim_query(list_of_query_strings)
    else:
        list_of_trimmed_query_strings = list_of_query_strings

    list_of_query_dicts = []
    for query_str in list_of_trimmed_query_strings:
        list_of_query_dicts.append({'query': query_str})

    tasks = []

    semaphore = asyncio.Semaphore(concurrent_tasks)
    logger.info('# {} tasks send to event loop'.format(len(list_of_query_dicts)))
    for query_dict in list_of_query_dicts:
        # pass Semaphore and session to every POST request
        task = asyncio.create_task(_post(query_dict, graphql_connection_, semaphore))
        tasks.append(task)

    responses = await asyncio.gather(*tasks)
    results = _handle_responses(responses)

    return results


def _handle_responses(responses):
    # check if there were errors reported by graph cool
    for res in responses:
        if 'errors' in res:
            logger.error(res['errors'])
            raise Exception(
                'query was not successfull --- exiting\n {}'.format(res))
    # concatenate batches
    results = []

    for res in responses:
        try:
            for batch_content in res['data'].values():
                if type(batch_content) is dict:
                    results.append(batch_content)
                elif type(batch_content) is list:  # when list
                    results.extend(batch_content)
        except (RuntimeError, AttributeError, TypeError):
            raise GraphQLException('Something went wrong\n {}'.format(res))

    return results


def do_trim_query(list_of_query_strings: list):
    list_of_trimmed_query_strings = []
    for query_str in list_of_query_strings:
        list_of_trimmed_query_strings.append(strip_whitespace_and_newlines(query_str))

    return list_of_trimmed_query_strings


async def _post(query, graphql_connection_, semaphore, backoff_interval=1.0, max_retries=10):
    headers = {
        'Accept': 'application/json',
        'content-type': 'application/json'
    }

    token = graphql_connection_.token
    if token is not None:
        headers['Authorization'] = 'Bearer {}'.format(token)

    status = -1
    while status != 200:
        retries = 0
        async with semaphore:
            async with graphql_connection_.session.post(graphql_connection_.endpoint, data=json.dumps(query), headers=headers) as response:
                status = response.status
                if status == 200:
                    return await response.json(content_type=None)
                logger.warning('non successfull post\n {}\n. status: {}\nSleeping for {} s and try again'.format(json.dumps(query), status, backoff_interval))
                retries += 1
                await asyncio.sleep(backoff_interval * retries)
                if retries > max_retries:
                    response.raise_for_status()


def strip_whitespace_and_newlines(input_string):
    input_string = input_string.replace('\n', '')
    input_string = input_string.replace(' ', '')
    return input_string


class GraphQLException(Exception):
    def __init___(self, message):
        Exception.__init__(
            self, "GraphQLException was raised with arguments {0}".format(message))
        self.message = message


class GraphQLDocumentNotFoundError(GraphQLException):
    def __init__(self, doc_id, message):
        self.doc_id = doc_id
        super(GraphQLDocumentNotFoundError, self).__init__('{}\nDocument with id {} not found'.format(message, doc_id))


class GraphQLFilesNotFoundError(GraphQLException):
    def __init__(self, file_id, message):
        self.doc_id = file_id
        super(GraphQLFilesNotFoundError, self).__init__('{}\nFile with id {} not found'.format(message, file_id))
