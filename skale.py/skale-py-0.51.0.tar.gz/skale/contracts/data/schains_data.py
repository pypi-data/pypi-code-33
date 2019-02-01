from Crypto.Hash import keccak

from skale.contracts import BaseContract
from skale.utils.helper import format, ip_from_bytes, public_key_to_address
from skale.utils.helper import sign_and_send


FIELDS = [
    'name',
    'owner',
    'indexInOwnerList',
    'partOfNode',
    'lifetime',
    'startDate',
    'deposit'
]


class SChainsData(BaseContract):
    def __get_raw(self, name):
        return self.contract.functions.schains(name).call()

    @format(FIELDS)
    def get(self, id):
        return self.__get_raw(id)

    @format(FIELDS)
    def get_by_name(self, name):
        id = self.name_to_id(name)
        return self.__get_raw(id)

    def get_schains_for_owner(self, account):
        schains = []
        list_size = self.get_schain_list_size(account)

        for i in range(0, list_size):
            id = self.get_schain_id_by_index_for_owner(account, i)
            schain = self.get(id)
            schains.append(schain)
        return schains

    def get_schain_list_size(self, account):
        return self.contract.functions.getSchainListSize(account).call({'from': account})

    def get_schain_id_by_index_for_owner(self, account, index): # for owner
        return self.contract.functions.schainIndexes(account, index).call()

    def get_schain_by_index(self, index):
        return self.contract.functions.getSchainByIndex(index).call()

    def get_nodes_for_schain_config(self, name):
        nodes_info = []
        nodes = self.get_nodes_for_schain(name)

        for i, node in enumerate(nodes):
            pk = node['publicKey'].hex()

            node_info = {
                'schainIndex': i,
                'nodeID': node['id'],
                'ip': ip_from_bytes(node['ip']),
                'basePort': node['port'],
                'publicKey': pk,
                'publicIP': ip_from_bytes(node['publicIP']),
                'owner': public_key_to_address(pk)
            }
            nodes_info.append(node_info)
        return nodes_info

    def get_nodes_for_schain(self, name):
        nodes = []
        ids = self.get_node_ids_for_schain(name)
        for id in ids:
            node = self.skale.nodes_data.get(id)
            node['id'] = id
            nodes.append(node)
        return nodes

    def get_node_ids_for_schain(self, name):
        id = self.name_to_id(name)
        return self.contract.functions.getNodesInGroup(id).call()

    def get_schain_ids_for_node(self, node_id):
        # return self.contract.functions.schainsForNodes(int(node_id)).call() # todo: new function - problem with bytes32 map
        return self.contract.functions.getSchainIdsForNode(node_id).call()  # todo: function will be removed

    def get_schains_for_node(self, node_id):
        schains = []
        #schain_contract = self.skale.get_contract_by_name('schains_data')
        schain_ids = self.get_schain_ids_for_node(node_id)
        for schain_id in schain_ids:
            # name = self.get_schain_name_by_schain_id(schain_id)
            schain = self.get(schain_id)
            schains.append(schain)
        return schains

    def get_schain_price(self, indexOfType):
        return self.contract.functions.getSchainPrice(indexOfType).call()

    def name_to_id(self, name):
        keccak_hash = keccak.new(data=name.encode("utf8"), digest_bits=256)
        return keccak_hash.hexdigest()