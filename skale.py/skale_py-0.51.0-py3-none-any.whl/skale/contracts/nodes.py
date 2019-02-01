import socket
from Crypto.Hash import keccak
from skale.contracts import BaseContract
from skale.utils.helper import format
from skale.utils.helper import sign_and_send

FIELDS = ['name', 'ip', 'port', 'owner', 'start_date', 'leaving_date', 'last_reward_date', 'second_address']
COMPACT_FIELDS = ['schainIndex', 'nodeID', 'ip', 'basePort']

class Nodes(BaseContract):

    def __get_raw(self, node_id):
        # return self.contract.functions.getNode(node_id).call()
        return self.contract.functions.nodes(node_id).call()

    @format(FIELDS)
    def get(self, node_id):
        return self.__get_raw(node_id)

    def get_active_node_ids(self):
        return self.contract.functions.getActiveNodeIds().call()

    def get_active_node_ips(self):
        return self.contract.functions.getActiveNodeIPs().call()

    def get_active_nodes_by_address(self, account):
        return self.contract.functions.getActiveNodesByAddress().call({'from': account})

    def node_name_to_id(self, name):
        keccak_hash = keccak.new(data=name.encode("utf8"), digest_bits=256)
        return keccak_hash.hexdigest()

    def is_node_name_available(self, name):
        node_id = self.node_name_to_id(name)
        return not self.contract.functions.nodesNameCheck(node_id).call()

    def is_node_ip_available(self, ip):
        ip_bytes = socket.inet_aton(ip)
        return not self.contract.functions.nodesIPCheck(ip_bytes).call()

    def authorized(self, address):
        return self.contract.functions.authorized(address).call()

    def add_authorized(self, address, wallet):
        op = self.contract.functions.addAuthorized(address)
        tx = sign_and_send(self.skale, op, 100000, wallet)
        return {'tx': tx}