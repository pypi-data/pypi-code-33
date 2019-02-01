from Crypto.Hash import keccak

from skale.contracts import BaseContract


class ContractManager(BaseContract):

    def get_contract_address(self, name):
        contract_hash = self.get_contract_hash_by_name(name)
        return self.contract.functions.contracts(contract_hash).call()

    def get_contract_hash_by_name(self, name):
        keccak_hash = keccak.new(data=name.encode("utf8"), digest_bits=256)
        return keccak_hash.hexdigest()
