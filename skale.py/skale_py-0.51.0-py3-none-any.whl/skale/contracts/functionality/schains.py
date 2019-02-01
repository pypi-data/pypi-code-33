from skale.contracts import BaseContract
from skale.utils.helper import ip_from_bytes


class SChains(BaseContract):

    def get_schain_by_index(self, index):  # todo: not found at ABI
        return self.contract.functions.getSchainByIndex(index).call()

    def get_schain_price(self, indexOfType, lifetime):
        return self.contract.functions.getSchainPrice(indexOfType, lifetime).call()
