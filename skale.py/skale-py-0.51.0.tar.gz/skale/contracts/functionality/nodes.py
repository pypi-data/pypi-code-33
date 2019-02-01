from Crypto.Hash import keccak
from skale.contracts import BaseContract


class Nodes(BaseContract):

    def node_name_to_id(self, name):
        keccak_hash = keccak.new(data=name.encode("utf8"), digest_bits=256)
        return keccak_hash.hexdigest()
