import requests
import os
import json
from .utils import validate_sha256hash, query_yes_no
from .errors import *

RPC_USER = os.environ.get("RPC_USER", "admin")
RPC_PASS = os.environ.get("RPC_PASS", "admin")
RPC_HOST = os.environ.get("RPC_HOST", "http://localhost:5516/")
# Known errors

CLIENT_AGENT = "StakeShareClient/v0.1"

VALID_METHODS = [
    # Wallet methods
    "getbalance",
    "getwalletinfo",
    "validateaddress",
    "walletpassphrase",
    "walletlock",
    "verifymessage",
    "signmessage",
    "addmultisigaddress",
    "getnewaddress",
    "getreceivedbyaddress",
    "gettransaction",
    "importprivkey",
    "sendtoaddress",
    "listaddressgroupings",
    "dumpprivkey",
    "listunspent",

    # Account methods
    "getaccount",
    "getaccountaddress",
    "getaddressesbyaccount",
    "listaccounts",

    # Staking methods
    "getstakesplitthreshold",
    "setstakesplitthreshold",
    "getstakingstatus",

    # Blockchain methods
    "getblock",
    "getblockchaininfo",
    "getblockcount",
    "getblockhash",
    "getblockheader",
    "verifychain",
    "getinfo",
    "getnextsuperblock",

    # Network difficulty
    "getdifficulty",
    "getnetworkhashps",
    "getmempoolinfo",
    "getmininginfo",
    "getnettotals",
    "getnetworkinfo",
    "getpeerinfo",
    "ping",

    # Transaction methods
    "getmempoolinfo",
    "gettxout",
    "settxfee",
    "gettxoutsetinfo",
    "getrawtransaction",
    "reservebalance",
    "decoderawtransaction",
    "decodescript",

    # Nodes methods
    "addnode",
    "getconnectioncount",

    # Master Nodes methods
    "getmasternodecount",
    "getmasternodeoutputs",
    "getmasternodescores",
    "getmasternodestatus",
    "getmasternodewinners",
    "listmasternodes",
    "getpoolinfo",
]
class StakeShareClient:

    client = requests.Session()
    _host = None
    _block_time = 60
    def __init__(self, user=None, password=None, host=None, block_time=None):
        self.client.auth = (user or RPC_USER, password or RPC_PASS)
        self._host = host or RPC_HOST
        self._block_time = block_time or 60

    def __request(self, method=None, params=[], raise_exception=True):
        if method not in VALID_METHODS:
            raise Exception("Please pass a valid method !")
        request_body = {
            "jsonrpc": "2.0",
            "id": CLIENT_AGENT,
            "method": method,
            "params": list(params)
        }
        result = self.client.post(self._host, data=json.dumps(request_body)).json()
        if result["error"] is not None and raise_exception:
            raise Exception("Error while calling method '%s' with params '%s': %s"% (
                method, params, result["error"]
            ))
        return result.get("result"), result.get("error")

    # Blockchain methods
    def get_block(self, hash):
        # Validate TXID as a sha256 hash
        validate_sha256hash(hash)
        params = [hash]
        result, _ = self.__request("getblock", params)
        return result
    def get_blockchain_info(self):
        result, _ = self.__request("getblockchaininfo")
        return result
    def get_block_count(self):
        result, _ = self.__request("getblockcount")
        return result
    def get_block_hash(self, height):
        params = [height]
        result, _ = self.__request("getblockhash", params)
        return result
    def get_block_header(self, hash):
        # Validate TXID as a sha256 hash
        validate_sha256hash(hash)
        params = [hash]
        result, _ = self.__request("getblockheader", params)
        return result
        return result
    def verify_chain(self, block_numbers=0):
        """
        Verifies blockchain database.
        - block_numbers : The number of blocks to check (default all)
        """
        response = query_yes_no("Are you sur you want to verify %s of the blockchain database ?" % block_numbers, "no")
        if response :
            print("This might take some time, please do not interrupt the function !")
            params = [block_numbers]
            result, _ = self.__request("verifychain", params)
            return result
        else:
            return "Stopped"
        return result
    def get_info(self):
        """
        Returns detailed informations about the actual state.
        """
        result, _ = self.__request("getinfo")
        return result
    def get_next_superblock(self):
        """
        Returns the next SuperBlock height.
        """
        result, _ = self.__request("getnextsuperblock")
        return result
    def get_time_to_next_superblock(self):
        """
        Return the estimated time in seconds until the next SuperBlock.
        """
        return (self.get_next_superblock() - self.get_block_count()) * self._block_time

    # Network methods
    def get_network_difficulty(self):
        params = []
        result, _ = self.__request("getdifficulty", params)
        return result
    def get_network_hps(self, block_numbers=120, height=-1):
        """
        Returns the estimated network hashes per second based on the last n blocks.
        - blocks: Number of block (default: 120) (if =-1 since last difficulty change) .
        - height: to estimate the network speed at the time when a certain block was found.
        """
        params = [block_numbers, height]
        result, _ = self.__request("getnetworkhashps", params)

        return result
    def get_mempool_info(self):
        params = []
        result, _ = self.__request("getmempoolinfo", params)
        return result
        return result
    def get_mining_info(self):
        result, _ = self.__request("getmininginfo")
        return result
    def get_network_stats(self):
        """
        Returns information about network traffic, bytes IN/OUT and current time.
        """
        params = []
        result, _ = self.__request("getnettotals", params)
        return result
    def get_p2p_network_stats(self):
        """
        Get Peer to Peer network stats.
        """
        params = []
        result, _ = self.__request("getnetworkinfo", params)
        return result
    def get_peer_info(self):
        """
        Returns data about each connected network node.
        """
        params = []
        result, _ = self.__request("getpeerinfo", params)
        return result
    def ping_peers(self):
        """
        Returns data about each connected network node.
        """
        params = []
        result, _ = self.__request("ping", params)
        return result

    # Transactions methods
    def get_unspent_txout(self, txid, vout, include_mempool=True):
        """
        Returns details about an unspent transaction output.
        - txid : Valid transaction ID
        - vout : The vector of an output (reffer to http://learnmeabitcoin.com/glossary/vout)
        """
        # Validate TXID as a sha256 hash
        validate_sha256hash(txid)
        params = [txid, vout, include_mempool]
        result, _ = self.__request("gettxout", params)
        return result
    def get_txout_stats(self):
        """
        Returns statistics about the unspent transaction output set.
        Note this call may take some time.
        return:
        {
          "height"            -> the height of the block up to which the UTXO set is accurate
          "bestblock"         -> the hash of the block up to which the UTXO is accurate.
          "transactions"      -> the number of distinct transactions to which the unspent outputs belong
          "txouts"            -> the number of unspent outputs
          "bytes_serialized"  -> how large the database is in bytes, should we serialize it
          "hash_serialized"   -> the hash of the entire serialized database (can be used to verify the UTXO set's integrity with other nodes)
          "total_amount"      -> This is the best possible guess for the amount of currency in circulation.
        }
        """
        # Validate TXID as a sha256 hash
        result, _ = self.__request("gettxoutsetinfo")
        return result
    def decode_raw_transaction(self, tx_hex_string):
        """
        Return a JSON object representing the serialized, hex-encoded transaction.
        """
        params = [tx_hex_string]
        result, _ = self.__request("decoderawtransaction", params)
        return result
    def decode_script(self, script_hex_string):
        """
        Decode a hex-encoded script.
        """
        params = [script_hex_string]
        result, _ = self.__request("decodescript", params)
        return result
    def get_raw_transaction(self, txid, simplified=True):
        """
        Return the raw transaction data.
        - txid: Transaction ID
        NOTE: To make it always work, you need to maintain a transaction index,
        using the -txindex command line option in.
        """
        if simplified:
            verbose = 0
        else:
            verbose = 1
        params = [txid, verbose]
        result, _ = self.__request("getrawtransaction", params)
        return result
    def send_raw_transaction(self, tx_hex_string, allow_high_fees=False):
        """
        Submits raw transaction (serialized, hex-encoded) to local node and network.
        - tx_hex_string: The hex string of the raw transaction
        - allow_high_fees: Whether or not to allow high fees
        """
        params = [tx_hex_string, allow_high_fees]
        result, _ = self.__request("sendrawtransaction", params)
        return result

    # Account methods
    def get_address_account(self, address):
        """
        Returns the account associated with the given address.
        """
        params = [address]
        result, _ = self.__request("getaccount", params)
        return result
    def list_accounts(self):
        params = []
        result, _ = self.__request("listaccounts", params)
        return result
    def get_account_address(self, account=""):
        params = [account]
        result, _ = self.__request("getaccountaddress", params)
        return result
    def list_account_addresses(self, account=""):
        """
        Returns the list of addresses for the given account.
        """
        params = [account]
        result, _ = self.__request("getaddressesbyaccount", params)
        return result
    def get_account_balance(self, account):
        result = self.list_accounts()

        # Will return None if the account does not exists
        return result.get(account)

    # Staking methods
    def get_stake_split_threshold(self):
        params = []
        result, _ = self.__request("getstakesplitthreshold", params)
        return result
    def set_stake_split_threshold(self, threshold):
        params = [threshold]
        result, _ = self.__request("setstakesplitthreshold", params)
        return result
    def get_staking_details(self):
        params = []
        result, _ = self.__request("getstakingstatus", params)
        return result
    def is_staking_enabled(self):
        params = []
        result, _ = self.__request("getstakingstatus", params)
        return result["staking status"]

    # Wallet methods
    def get_balance(self, account="*", confirmations=1, include_watch_only=False):
        params = [account, confirmations, include_watch_only]
        result, _ = self.__request("getbalance", params)
        return result
    def get_wallet_info(self):
        result, _ = self.__request("getwalletinfo")
        return result
    def __get_reserve_balance(self):
        result, _ = self.__request("reservebalance")
        return result
    def get_reserved_balance(self):
        result = self.__get_reserve_balance()
        return result["amount"]
    def get_reserved_amount(self):
        result = self.__get_reserve_balance()
        return result["amount"]
    def set_reserved_balance(self, amount):
        params = [amount]
        result, _ = self.__request("reservebalance", params)
        return result
    def validate_address(self, address):
        """
        Get information about an address.
        - address: The address to validate
        """
        params = [address]
        result, _ = self.__request("validateaddress", params)
        return result
    def unlock_wallet(self, passphrase, duration=30):
        """
        Unlock an encrypted wallet for sepcific duration
        - passphrase: Wallet passphrase
        - duration: Amount of seconds to keep the wallet unlocked (default: 30s)
        """
        params = [passphrase, duration]
        result, _ = self.__request("walletpassphrase", params)
        return result
    def lock_wallet(self):
        """
        Lock an encrypted wallet
        """
        params = []
        result, _ = self.__request("walletlock", params)
        return result
    def verify_message(self, address, signature, message):
        """
        Verify a signed message
        - address: The address used to sign the message
        - signature: The signature to check
        - message: The message to verify
        """
        params = [address, signature, message]
        result, _ = self.__request("verifymessage", params)
        return result
    def sign_message(self, message):
        """
        Sign a message using your private of a specifique address
        - address: The address used to sign the message
        - message: The clear message to sign
        """
        params = [address, message]
        result, _ = self.__request("signmessage", params)
        return result
    def add_multisig_address(self, required_sig, addresses, account=None):
        """
        Add a multi-signature address to the wallet
        - address: The address used to sign the message
        - message: The clear message to sign
        """
        params = [required_sig]
        if isinstance(addresses, list, tuple) and len(addresses) > 1:
            params.append(json.dumps(addresses))
        else:
            raise Exception("Argument address is invalid, should be a list type and with 2 or more address!")

        if account is not None:
            params.append(account)
        result, _ = self.__request("addmultisigaddress", params)
        return result
    def get_recieved_by_address(self, address, min_confirmation=10):
        """
        Returns the total amount received by the given address in transactions
        with at least minconf confirmations.
        """
        params = [address, min_confirmation]
        result, _ = self.__request("getreceivedbyaddress", params)
        return result
    def get_new_address(self, account=None):
        """
        Returns a new StakeShare address for receiving payments.
        If 'account' is specified (recommended), it is added to the address book
        so payments received with the address will be credited to 'account'.
        """
        params = []
        if account is not None:
            params.append(account)
        result, _ = self.__request("getnewaddress", params)
        return result
    def get_transaction(self, txid, include_watch_only=False):
        params = [txid, include_watch_only]
        result, _ = self.__request("gettransaction", params)
        return result
    def send_to(self, address, amount, comment=None, comment_to=None):
        """
        Send an amount to a given address. The amount is a real and is rounded
        to the nearest 0.00000001 .
        """
        params = [address, amount]
        if comment is not None:
            params.append(comment)
        if comment_to is not None:
            params.append(comment_to)

        result, _ = self.__request("sendtoaddress", params)
        return result
    def send_many(self, from_account, address_amount, min_confirmations=1):
        """
        Send multiple times. Amounts are double-precision floating point numbers.
        """
        params = [from_account, json.dumps(address_amount), min_confirmations]

        result, _ = self.__request("sendmany", params)
        return result
    def list_addresses_groups(self):
        params = []

        result, _ = self.__request("listaddressgroupings", params)

        return result
    def import_private_key(self, private_key, label="", rescan=True):
        params = [private_key, label, rescan]
        result, _ = self.__request("importprivkey", params)
        return result
    def __dump_private_key(self, address):
        params = [address]
        result, _ = self.__request("dumpprivkey", params, raise_exception=False)
        return result, _
    def is_address_owned(self, address):
        _, errors = self.__dump_private_key(address)
        if errors is not None and errors.get("code") == RPC_WALLET_ERROR:
            print ("Code %s " % errors.get("code") )
            return False

        return True
    def list_unspent(self, addresses=None, min_confirmations=1, max_confirmations=9999):
        """
        Returns array of unspent transaction outputs with between minconf and
        maxconf (inclusive) confirmations. Optionally filter to only include
        txouts paid to specified addresses.
        - min_confirmations: Minimum transactions
        - max_confirmations: Maximum transactions
        - address: Address list to use as filter
        """
        params = [min_confirmations, max_confirmations]

        if addresses is not None and isinstance(addresses, list) and len(addresses) > 0:
            params.append(addresses)
        result, _ = self.__request("listunspent", params)
        return result

    # Node methods
    def add_node(self, node):
        """
        Attempts to add a node to the addnode list
        - node : Node DNS or IP and Port (eg. 1.2.3.4:5515 or node.example.com:5515)
        """
        params = [node, "add"]
        result, _ = self.__request("addnode", params)
        return result
    def remove_node(self, node):
        """
        Attempts to remove a node to the addnode list
        - node : Node DNS or IP and Port (eg. 1.2.3.4:5515 or node.example.com:5515)
        """
        params = [node, "remove"]
        result, _ = self.__request("addnode", params)
        return result
    def connect_to_node(self, node):
        """
        Attempts to connect to a node only one time
        - node : Node DNS or IP and Port (eg. 1.2.3.4:5515 or node.example.com:5515)
        """
        params = [node, "onetry"]
        result, _ = self.__request("addnode", params)
        return result
    def get_connection_count(self):
        """
        Returns the number of connections to other nodes.
        """
        params = []
        result, _ = self.__request("getconnectioncount", params)
        return result

    # MasterNode methods
    def get_masternodes_count_stats(self):
        """
        Get count stats of the current MasterNodes
        """
        params = []
        result, _ = self.__request("getmasternodecount", params)
        return result
    def get_masternodes_txout(self):
        """
        Get my masternode transaction outputs
        """
        params = []
        result, _ = self.__request("getmasternodeoutputs", params)
        return result
    def get_masternodes_scores(self, blocks_count=25):
        """
        Get list of winning masternode by score for the last <blocks_count>
        - blocks_count: Limit to this last number of blocks
        """
        params = []
        result, _ = self.__request("getmasternodescores", params)
        return result
    def get_masternodes_status(self, blocks_count=25):
        """
        Get the status of the current MasterNode
        """
        params = []
        result, _ = self.__request("getmasternodestatus", params)
        return result
    def get_masternodes_winners(self, blocks_count=10, address=None):
        """
        Get the MasterNode winners for the last <blocks_count> blocks, with
        the possiblity of filtring by address <address_filter>
        - blocks_count: Limit to this last number of block (default: 10)
        - address: If set, will filter master nodes using this address
        """
        params = [blocks_count]
        if address_filter is not None:
            params.append(address)

        result, _ = self.__request("getmasternodewinners", params)
        return result
    def list_masternodes(self, filter=None):
        """
        Get the detailed list of MasterNodes in the network sorted by rank,
        and their diffrent status.
        - filter: If set this filter will be applied on txhash, status, or address.
        """
        params = []
        if filter is not None:
            params.append(filter)

        result, _ = self.__request("listmasternodes", params)
        return result
    def get_pool_info(self):
        """
        Get detailed information about the current pool
        """
        params = []

        result, _ = self.__request("getpoolinfo", params)
        return result
