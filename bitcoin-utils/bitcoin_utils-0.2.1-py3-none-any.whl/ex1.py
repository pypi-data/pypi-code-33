from binascii import hexlify

from bitcoinutils.constants import NETWORK_WIF_PREFIXES, NETWORK_P2PKH_PREFIXES, SIGHASH_ALL
from bitcoinutils.setup import setup, get_network
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.keys import Address, PrivateKey

def main():
    #setup('mainnet')
    #priv = PrivateKey()
    #print(priv.to_wif())
    #priv = PrivateKey(secret_exponent = 1)
    #priv = PrivateKey.from_wif('KwDiBf89QgGbjEhKnhXJuH7LrciVrZi3qYjgd9M7rFU73sVHnoWn')
    #message = "The test!"
    #pub = priv.get_public_key()
    #print(priv.to_wif())
    #print(pub.to_hex())
    #address = pub.get_address().to_address()
    #print(address)
    #signature = priv.sign_message(message)
    #print(signature)
    #print(message)
    #assert PublicKey.verify_message(address, signature, message)

    setup('testnet')
    txin = TxInput('fb48f4e23bf6ddf606714141ac78c3e921c8c0bebeb7c8abb2c799e9ff96ce6c', 0)
    #print(txin.serialize())
    addr = Address('n4bkvTyU1dVdzsrhWBqBw8fEMbHjJvtmJR')
    txout = TxOutput(0.1, ['OP_DUP', 'OP_HASH160', addr.to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG'])
    #addr = Address('2MxQYbQLegzGTQFy11d3ZM3X4pMLayXEErb')
    #txout = TxOutput(0.2, ['OP_HASH160', addr.to_hash160(), 'OP_EQUAL'])
    #change_addr = Address('mytmhndz4UbEMeoSZorXXrLpPfeoFUDzEp')
    change_addr = Address('mmYNBho9BWQB2dSniP1NJvnPoj5EVWw89w')

    #TODO 0.29 become 0.28999999
    #SOLVE THE AMOUNT ISSUE FIRST !!!
    change_txout = TxOutput(0.29, ['OP_DUP', 'OP_HASH160', change_addr.to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG'])
    #print(txout.serialize())
    tx = Transaction([txin], [txout, change_txout])
    print(tx.serialize())

    sk = PrivateKey('cRvyLwCPLU88jsyj94L7iJjQX5C2f8koG4G2gevN4BeSGcEvfKe9')
    from_addr = Address('myPAE9HwPeKHh8FjKwBNBaHnemApo3dw6e')
    sig = sk.sign_input(tx, 0, ['OP_DUP', 'OP_HASH160', from_addr.to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG'])
    print(sig)
    pk = sk.get_public_key()
    pk = pk.to_hex()
    print (pk)
    txin.script_sig = [sig, pk]
    signed_tx = tx.serialize()
    print(signed_tx)

    # privkey of the address myPAE9HwPeKHh8FjKwBNBaHnemApo3dw6e in the txin
    # (fb48f4e23bf6ddf606714141ac78c3e921c8c0bebeb7c8abb2c799e9ff96ce6c) is cRvyLwCPLU88jsyj94L7iJjQX5C2f8koG4G2gevN4BeSGcEvfKe9


if __name__ == "__main__":
    main()

