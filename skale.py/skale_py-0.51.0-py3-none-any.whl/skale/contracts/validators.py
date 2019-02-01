from skale.contracts import BaseContract
from skale.utils.helper import sign_and_send


class Validators(BaseContract):

    def get_periods(self, account):
        return self.contract.functions.getPeriods().call({'from': account})

    def get_validated_array(self, node_id, account):
        return self.contract.functions.getValidatedArray(node_id).call({'from': account})

    def add_authorized(self, address, wallet):
        op = self.contract.functions.addAuthorized(address)
        tx = sign_and_send(self.skale, op, 100000, wallet)
        return {'tx': tx}