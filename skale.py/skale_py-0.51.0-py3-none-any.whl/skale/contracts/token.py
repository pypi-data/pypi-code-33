from skale.contracts import BaseContract
from skale.utils.helper import sign_and_send
from skale.utils.constants import GAS

class Token(BaseContract):

    def transfer(self, address, value, wallet):
        op = self.contract.functions.transfer1(address, value)
        tx = sign_and_send(self.skale, op, GAS['token_transfer'], wallet)
        return {'tx': tx}

    def get_balance(self, address):
        return self.contract.functions.balanceOf(address).call()

    def add_authorized(self, address, wallet):
        op = self.contract.functions.addAuthorized(address)
        tx = sign_and_send(self.skale, op, GAS['token_transfer'], wallet)
        return {'tx': tx}