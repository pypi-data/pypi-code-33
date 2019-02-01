from web3 import Web3


class BaseContract:
    def __init__(self, skale, name, address, abi):
        self.skale = skale
        self.web3 = skale.web3
        self.name = name
        self.address = Web3.toChecksumAddress(address)
        self.abi = abi
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)
