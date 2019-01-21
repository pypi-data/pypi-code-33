"""
Official python library for Blockchair web services. 
Easily query the blockchain without writing any code. 
Fast, reliable, and packed with powerful features you won't find in other block explorers. 
Currently supports bitcoin, bitcoin-cash,bitcoin-sv,litecoin, ethereum.
"""

import json
import operator

from .exceptions import APIError
from .utils import *

api_key = None


class Blockchair():
    """Class for dificult calls with filters, sorts, limits, and offset can be used as a paginator."""

    _state = None

    def __init__(self):
        self.chain = BTC
        self.query = None
        self.sort = None
        self.limit = None
        self.offset = None

    chain = property(operator.attrgetter('_chain'))

    @chain.setter
    def chain(self, value):
        """

        :param str value: possible values are BSV, BTC, BCH, LTC, ETH.

        """
        is_valid_chain(value)
        self._chain = value

    query = property(operator.attrgetter('_query'))

    @query.setter
    def query(self, value):
        """

        :param list value: list of lists filters parametrs like `[['id',1,3,'strict'],['coinbase_data_bin','~','hello']]`.

        """
        value is None or is_valid_query(value)
        self._query = value

    sort = property(operator.attrgetter('_sort'))

    @sort.setter
    def sort(self, value):
        """

        :param list value: list of lists sorts parametrs like `[['id','desc'],['size','asc']]`.

        """
        value is None or is_valid_sort(value)
        self._sort = value


    limit = property(operator.attrgetter('_limit'))

    @limit.setter
    def limit(self, value):
        """

        :param int value: a natural number from 1 to 100.

        """
        value is None or is_valid_limit(value)
        self._limit = value

    offset = property(operator.attrgetter('_offset'))

    @offset.setter
    def offset(self, value):
        """

        :param int value:  is a natural number from 1 to 10000.

        """
        value is None or is_valid_offset(value)
        self._offset = value

    def _construct_call(self, resource, sort=None, querys=None):
        """A private function to construct http get-request.

        :param str resource: a main part of request.
        :param sort:  (Default value = None)
        :param querys:  (Default value = None)
        :return: str the result of request.

        """

        query = ''

        if sort is not None:
            sort = sort[0][0]+'('+sort[0][1]+'),'+sort[1][0]+'('+sort[1][1] + \
                          ')' if len(sort) == 2 else sort[0][0]+'('+sort[0][1]+')'

        if querys is not None:
            for q in querys:
                if len(q) == 2:
                    query += q[0] + '(' + str(q[1]) + '),'
                elif len(q) == 3:
                    if q[1] == '^' or q[1] == '~':
                        query += q[0] + '(' + str(q[1]) + str(q[2]) + '),'
                    elif q[2] == '<':
                        query += q[0] + '(...' + str(q[1]) + '),'
                    elif q[2] == '>':
                        query += q[0] + '(' + str(q[1]) + '...),'
                    elif q[2] == '<=':
                        query += q[0] + '(..' + str(q[1]) + '),'
                    elif q[2] == '>=':
                        query += q[0] + '(' + str(q[1]) + '..),'
                else:
                    if q[3] == 'strict':
                        query += q[0] + '(' + str(q[1]) + '...' + str(q[2]) + '),'
                    else:
                        query += q[0] + '(' + str(q[1]) + '..' + str(q[2]) + '),'
            else:
                query = query[:-1]

        if query:
            resource += '?q=' + query
            resource += ',id(..' + str(self._state) + \
                ')' if self._state and self.offset else ''
            resource += '&s=' + sort if sort else ''
            resource += '&limit=' + str(self.limit) if self.limit else ''
            resource += '&offset' + str(self.offset) if self.offset else ''
        elif sort:
            resource += '?s=' + sort
            resource += '&q=id(..' + str(self._state) + \
                ')' if self._state and self.offset else ''
            resource += '&limit=' + str(self.limit) if self.limit else ''
            resource += '&offset' + str(self.offset) if self.offset else ''
        elif self.limit:
            resource += '?limit=' + str(self.limit)
            resource += '&q=id(..' + str(self._state) + \
                ')' if self._state and self.offset else ''
            resource += '&offset' + str(self.offset) if self.offset else ''
        elif self.offset:
            resource += '?offset=' + str(self.offset)
            resource += '&q=id(..' + str(self._state) + \
                ')' if self._state else ''

        response = call_api(resource, chain=self.chain)
        json_response = json.loads(response)

        if not self._state:
            self._state = json_response['context']['state']

        return json_response

    def get_blocks(self, mempool=None):
        """Get a list of blocks that you find.

        :param str mempool: the request from mempool of blocks or no (Default value = None)

        """

        resource = '/mempool' if mempool else ''
        resource += '/blocks'

        if self.sort is None or len(self.sort) == 0:
            if self.query is None or len(self.query) == 0:
                return self._construct_call(resource)
            else:
                if self.chain is ETH:
                    is_valid_block_query(self.query, QUERY_BLOCK_LIST_ETH)
                elif self.chain is BSV or self.chain is BCH:
                    is_valid_block_query(self.query, QUERY_BLOCK_LIST_BCH_BSV)
                else:
                    is_valid_block_query(self.query)
        else:
            if self.query is None or len(self.query) == 0:
                if self.chain is ETH:
                    is_valid_block_sort(self.sort, SORT_BLOCK_LIST_ETH)
                elif self.chain is BSV or self.chain is BCH:
                    is_valid_block_sort(self.sort, SORT_BLOCK_LIST_BCH_BSV)
                else:
                    is_valid_block_sort(self.sort)
            else:
                if self.chain is ETH:
                    is_valid_block_sort(self.sort, SORT_BLOCK_LIST_ETH)
                    is_valid_block_query(self.query, QUERY_BLOCK_LIST_ETH)
                elif self.chain is BSV or self.chain is BCH:
                    is_valid_block_sort(self.sort, SORT_BLOCK_LIST_BCH_BSV)
                    is_valid_block_query(self.query, QUERY_BLOCK_LIST_BCH_BSV)
                else:
                    is_valid_block_sort(self.sort)
                    is_valid_block_query(self.query)

        return self._construct_call(resource, self.sort, self.query)

    def get_transactions(self, mempool=None):
        """Get a list of transactions in blocks that you find.

        :param mempool: the request from mempool of blocks or no (Default value = None)

        """

        resource = '/mempool' if mempool else ''
        resource = '/transactions'

        if self.sort is None or len(self.sort) == 0:
            if self.query is None or len(self.query) == 0:
                return self._construct_call(resource)
            else:
                if self.chain is ETH:
                    is_valid_tx_query(self.query, QUERY_TRANSACTION_LIST_ETH)
                elif self.chain is BSV or self.chain is BCH:
                    is_valid_tx_query(self.query,
                                      QUERY_TRANSACTION_LIST_BCH_BSV)
                else:
                    is_valid_tx_query(self.query)
        else:
            if self.query is None or len(self.query) == 0:
                if self.chain is ETH:
                    is_valid_tx_sort(self.sort, SORT_TRANSACTION_LIST_ETH)
                elif self.chain is BSV or self.chain is BCH:
                    is_valid_tx_sort(self.sort, SORT_TRANSACTION_LIST_BCH_BSV)
                else:
                    is_valid_tx_sort(self.sort)
            else:
                if self.chain is ETH:
                    is_valid_tx_sort(self.sort, SORT_TRANSACTION_LIST_ETH)
                    is_valid_tx_query(self.query, QUERY_TRANSACTION_LIST_ETH)
                elif self.chain is BSV or self.chain is BCH:
                    is_valid_tx_sort(self.sort, SORT_TRANSACTION_LIST_BCH_BSV)
                    is_valid_tx_query(self.query,
                                      QUERY_TRANSACTION_LIST_BCH_BSV)
                else:
                    is_valid_tx_sort(self.sort)
                    is_valid_tx_query(self.query)

        return self._construct_call(resource, self.sort, self.query)

    def get_outputs(self, mempool=None):
        """Get a list of outputs in blockchain.

        :param mempool: the request from mempool of blocks or no (Default value = None).
        :raises: APIError

        """

        if self.chain is ETH:
            raise APIError('Call outputs is not support ethereum.', 400)

        resource = '/mempool' if mempool else ''
        resource = '/outputs'

        if self.sort is None or len(self.sort) == 0:
            if self.query == None or len(self.query) == 0:
                return self._construct_call(resource)
            else:
                is_valid_output_query(self.query)
        else:
            if self.query is None or len(self.query) == 0:
                is_valid_output_sort(self.sort)
            else:
                is_valid_output_sort(self.sort)
                is_valid_output_query(self.query)

        return self._construct_call(resource, self.sort, self.query)

    def get_calls(self):
        """Get a list of ethereum calls.

        :raises: APIError

        """

        if not (self.chain is ETH):
            raise APIError(
                """Call outputs is support only ethereum. Please change 'chain' on ETH. """, 400)

        resource = '/calls'

        if self.sort is None or len(self.sort) == 0:
            if self.query == None or len(self.query) == 0:
                return self._construct_call(resource)
            else:
                is_valid_call_query(self.query)
        else:
            if self.query is None or len(self.query) == 0:
                is_valid_call_sort(self.sort)
            else:
                is_valid_call_sort(self.sort)
                is_valid_call_query(self.query)

        return self._construct_call(resource, self.sort, self.query)

    def get_uncles(self):
        """Get a list of ethereum uncles.

        :raises: APIError

        """

        if not (self.chain is ETH):
            raise APIError(
                """Call uncles is support only ethereum. Please change 'chain' on ETH. """, 400)

        resource = '/uncles'

        if self.sort is None or len(self.sort) == 0:
            if self.query == None or len(self.query) == 0:
                return self._construct_call(resource)
            else:
                is_valid_uncle_query(self.query)
        else:
            if self.query is None or len(self.query) == 0:
                is_valid_uncle_sort(self.sort)
            else:
                is_valid_uncle_sort(self.sort)
                is_valid_uncle_query(self.query)

        return self._construct_call(resource, self.sort, self.query)

    def clear_state(self):
        """Сlear out the number of state for new request."""
        self._state = None


def get_latest_block(chain=BTC, api_key=api_key):
    """Get the latest block hash for a given coin.

    :param api_key:  (Default value = api_key)
    :param str chain: chain to look up, possible values are BSV, BTC, BCH, LTC, ETH
    :return dict: the latest block info. If chain ethereum return array of last 6 blocks.

    """
    is_valid_chain(chain)

    resource = '/mempool/blocks'
    response = call_api(resource, chain=chain)
    json_response = json.loads(response)
    if chain == 'ethereum':
        last_six_blocks = search_value(json_response, 'data')
        return last_six_blocks
    latest_block = search_value(json_response, 'data')
    return latest_block[0]


def get_block(block_info, chain=BTC, api_key=api_key):
    """Takes a block_info and returns the block and addition information.

    :param str: chain: chain to look up, possible values are BSV, BTC, BCH, LTC, ETH
    :param int: or str block_info: a block id(int) or hash(str) that you want know the block
    :return dict: the block and transactions in block (only for Ethereum - synthetic_transactions,uncles) what you find
    :param block_info: 
    :param chain:  (Default value = BTC)
    :param api_key:  (Default value = api_key)

    """
    is_valid_chain(chain)

    if chain is ETH:
        if isinstance(block_info, int):
            is_valid_block_num(block_info)
        else:
            is_valid_ethereum_hash(block_info)
    else:
        if isinstance(block_info, int):
            is_valid_block_num(block_info)
        else:
            is_valid_hash(block_info)

    resource = '/dashboards/block/' + str(block_info)
    response = call_api(resource, chain=chain)
    json_response = json.loads(response)

    if not json_response['data']:
        return {}

    if block_info == 0:
        return json_response['data']

    block = json_response['data'][str(block_info)]
    return block


def get_blocks(block_info_list, chain=BTC, api_key=api_key):
    """Takes a list block_info_list and returns the blocks and addition information.

    :param str: chain: chain to look up, possible values are BSV, BTC, BCH, LTC, ETH
    :param list: block_info_list: a list of block id(int) or hash(str) that you want know the blocks
    :return dict: the blocks and transactions in blocks (only for Ethereum - synthetic_transactions,uncles) what you find
    :param block_info_list: 
    :param chain:  (Default value = BTC)
    :param api_key:  (Default value = api_key)

    """
    is_valid_chain(chain)

    for block_info in block_info_list:
        if chain is ETH:
            if isinstance(block_info, int):
                is_valid_block_num(block_info)
            else:
                is_valid_ethereum_hash(block_info)
        else:
            if isinstance(block_info, int):
                is_valid_block_num(block_info)
            else:
                is_valid_hash(block_info)

    resource = '/dashboards/blocks/'

    for block_info in block_info_list:
        resource += str(block_info) + ','

    resource = resource[:-1]
    response = call_api(resource, chain)
    json_response = json.loads(response)

    if not json_response['data']:
        return {}

    blocks = json_response['data']
    return blocks


def get_transaction(tx_info, chain=BTC, api_key=api_key):
    """Takes a tx_info and returns an array with identifiers or hashes of transactions used as keys, and arrays of elements as keys.

    :param str: chain: chain to look up, possible values are BSV, BTC, BCH, LTC, ETH
    :param int: or str tx_info: an internal blockchair-id(int) or a hash of a transaction(str) that you want know the transaction
    :return dict: the transaction what you find
    :param tx_info: 
    :param chain:  (Default value = BTC)
    :param api_key:  (Default value = api_key)

    """
    is_valid_chain(chain)

    if chain is ETH:
        if isinstance(tx_info, int):
            is_valid_blockchair_id(tx_info)
        else:
            is_valid_ethereum_hash(tx_info)
    else:
        if isinstance(tx_info, int):
            is_valid_blockchair_id(tx_info)
        else:
            is_valid_hash(tx_info)

    resource = '/dashboards/transaction/' + str(tx_info)
    response = call_api(resource, chain=chain)
    json_response = json.loads(response)

    if not json_response['data']:
        return {}

    if tx_info == 0:
        return json_response['data']

    tx = json_response['data'][str(tx_info)]
    return tx


def get_transactions(tx_info_list, chain=BTC, api_key=api_key):
    """Takes a list tx_info_list and returns an array with identifiers or hashes of transactions used as keys, and arrays of elements as keys.

    :param str: chain: chain to look up, possible values are BSV, BTC, BCH, LTC, ETH
    :param list: tx_info_list: a list of an internal blockchair-id(int) or a hash of a transactions(str) that you want know the transactions
    :return dict: the transactions what you find
    :param tx_info_list: 
    :param chain:  (Default value = BTC)
    :param api_key:  (Default value = api_key)

    """
    is_valid_chain(chain)

    for tx_info in tx_info_list:
        if chain is ETH:
            if isinstance(tx_info, int):
                is_valid_blockchair_id(tx_info)
            else:
                is_valid_ethereum_hash(tx_info)
        else:
            if isinstance(tx_info, int):
                is_valid_blockchair_id(tx_info)
            else:
                is_valid_hash(tx_info)

    resource = '/dashboards/transactions/'

    for tx_info in tx_info_list:
        resource += str(tx_info) + ','

    resource = resource[:-1]
    response = call_api(resource, chain)
    json_response = json.loads(response)

    if not json_response['data']:
        return {}

    txs = json_response['data']
    return txs


def get_priority(tx_hash, chain=BTC, api_key=api_key):
    """Takes a tx_hash for mempool transactions shows priority (position) (for Bitcoin - by fee_per_kwu, for Bitcoin Cash - by fee_per_kb,
    for Ethereum - by gas_price) over other transactions (out_of mempool transactions).

    :param str: chain: chain to look up, possible values are BSV, BTC, BCH, LTC, ETH
    :param str: tx_hash: a hash of an unconfirmed transaction
    :return dict: the unconfirmed transaction priority what you find
    :param tx_hash: 
    :param chain:  (Default value = BTC)
    :param api_key:  (Default value = api_key)

    """
    is_valid_chain(chain)

    if chain is ETH:
        is_valid_ethereum_hash(tx_hash)
    else:
        is_valid_hash(tx_hash)

    resource = '/dashboards/transaction/' + tx_hash + '/priority'
    response = call_api(resource, chain=chain)
    json_response = json.loads(response)

    if not json_response['data']:
        return {}

    priority = json_response['data'][tx_hash]
    return priority


def get_address(address, chain=BTC, api_key=api_key):
    """Takes an address returns an array with one element (if the address is found), in that case the address is the key,
     and the value is an array consisting of the following elements

    :param str: chain: chain to look up, possible values are BSV, BTC, BCH, LTC, ETH
    :param str: address: a coin address
    :return dict: the address info what you find
    :param address: 
    :param chain:  (Default value = BTC)
    :param api_key:  (Default value = api_key)

    """
    is_valid_chain(chain)

    if chain is ETH:
        is_valid_ethereum_addr(tx_hash)
    else:
        is_valid_addr(tx_hash)

    resource = '/dashboards/address/' + address
    response = call_api(resource, chain=chain)
    json_response = json.loads(response)

    if not json_response['data']:
        return {}

    addr = json_response['data']
    return addr


def get_uncle(uncle_hash, api_key=api_key):
    """Takes an uncle_hash and returns the information about uncle

    :param str: uncle_hash: the uncle hash that you find the uncle
    :return dict: the uncle what you find
    :param uncle_hash: 
    :param api_key:  (Default value = api_key)

    """
    is_valid_ethereum_hash(uncle_hash)

    resource = '/dashboards/uncle/' + uncle_hash
    response = call_api(resource, chain=ETH)
    json_response = json.loads(response)

    if not json_response['data']:
        return {}

    uncle = json_response['data'][uncle_hash]
    return uncle


def get_uncles(uncle_hash_list, api_key=api_key):
    """Takes a list of uncle_hash and returns the information about uncles

    :param list: uncle_hash_list: the list of uncle hash(str) that you find the uncles
    :return dict: the uncles what you find
    :param uncle_hash_list: 
    :param api_key:  (Default value = api_key)

    """
    for uncle_hash in uncle_hash_list:
        is_valid_ethereum_hash(uncle_hash)

    resource = '/dashboards/uncles/'

    for uncle_hash in uncle_hash_list:
        resource += uncle_hash + ','

    resource = resource[:-1]
    response = call_api(resource, chain=ETH)
    json_response = json.loads(response)

    if not json_response['data']:
        return {}

    uncles = json_response['data']
    return uncles


def get_stats(chain=BTC, api_key=api_key):
    """Get the stats for a given coin

    :param str: chain: chain to look up, possible values are BSV, BTC, BCH, LTC, ETH
    :return dict: returns a dictinary with blockchain statistics
    :param chain:  (Default value = BTC)
    :param api_key:  (Default value = api_key)

    """
    is_valid_chain(chain)

    resource = '/stats'
    response = call_api(resource, chain=chain)
    json_response = json.loads(response)
    stats = json_response['data']
    return stats


def get_nodes(chain=BTC, api_key=api_key):
    """Get the nodes for a given coin

    :param str: chain: chain to look up, possible values are bitcoin-sv, bitcoin, bitcoin-cash,litecoin,
    :return dict: returns data on networks stats
    :param chain:  (Default value = BTC)
    :param api_key:  (Default value = api_key)

    """
    is_valid_chain(chain)

    if chain is ETH:
        raise APIError('Call nodes is not support ethereum', 404)

    resource = '/nodes'
    response = call_api(resource, chain=chain)
    json_response = json.loads(response)
    nodes = json_response['data']
    return nodes


def push_broadcast_tx(tx, chain=BTC, api_key=api_key):
    """Takes a signed transaction hex binary (and chain) and broadcasts it to the chain network.

    :param str: tx: hex encoded transaction
    :param str: chain: chain to look up, possible values are BSV, BTC, BCH, LTC, ETH
    :return dict: returns a dictinary with transaction hash or error 400
    :param tx: 
    :param chain:  (Default value = BTC)
    :param api_key:  (Default value = api_key)

    """
    is_valid_chain(chain)

    data = {'data': tx}
    resource = '/push/transaction'
    response = call_api(resource, data=data, chain=chain)
    json_response = json.loads(response)
    return json_response


def get_raw_tx(tx_hash, chain=BTC, api_key=api_key):
    """Takes an transaction hash and returns the hex raw transaction

    :param str: tx_hash: the uncle hash that you find the uncle
    :return dict: the raw transaction what you find
    :param tx_hash: 
    :param chain:  (Default value = BTC)
    :param api_key:  (Default value = api_key)

    """
    is_valid_chain(chain)

    resource = '/raw/transaction/' + tx_hash
    response = call_api(resource, chain=chain)
    json_response = json.loads(response)
    raw_tx = json_response['data'][tx_hash]
    return raw_tx
