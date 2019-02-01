import json, socket, os
from random import randint
import ipaddress
from time import sleep
import logging
import yaml
import string, random

from eth_keys import keys
from web3 import Web3

from skale.config import SKALE_ENVS_FILEPATH, ENVS_DIR, ENV_FILE_EXTENSION
from skale.blockchain_env import BlockchainEnv

logger = logging.getLogger(__name__)


def format(fields):
    """
        Transform array to object with passed fields
        Usage:
        @format(['field_name1', 'field_name2'])
        def my_method()
            return [0, 'Test']

        => {'field_name1': 0, 'field_name2': 'Test'}
    """

    def real_decorator(function):
        def wrapper(*args, **kwargs):
            result = function(*args, **kwargs)
            obj = {}
            for i, field in enumerate(fields):
                obj[field] = result[i]
            return obj

        return wrapper

    return real_decorator


def get_receipt(web3, tx):
    return web3.eth.getTransactionReceipt(tx)


def get_eth_nonce(web3, address):
    return web3.eth.getTransactionCount(address)


def get_nonce(skale, address):
    lib_nonce = skale.nonces.get(address)
    if not lib_nonce:
        lib_nonce = get_eth_nonce(skale.web3, address)
        skale.nonces.get(address)
    else:
        lib_nonce += lib_nonce
    return lib_nonce


def sign_and_send(skale, method, gas_amount, wallet):
    eth_nonce = get_nonce(skale, wallet['address'])
    txn = method.buildTransaction({
        'gas': gas_amount,
        'nonce': eth_nonce #+ 2
    })
    signed_txn = skale.web3.eth.account.signTransaction(txn, private_key=wallet['private_key'])
    tx = skale.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    logger.info(f'{method.__class__.__name__} - transaction_hash: {skale.web3.toHex(tx)}')
    return tx


def await_receipt(web3, tx, retries=10, timeout=5):
    for _ in range(0, retries):
        receipt = get_receipt(web3, tx)
        if (receipt != None):
            return receipt
        sleep(timeout)
    return None


def ip_from_bytes(bytes):
    return socket.inet_ntoa(bytes)


def ip_to_bytes(ip):
    return socket.inet_aton(ip)


def check_port(port):
    if port not in range(1, 65535):
        raise ValueError(f'{port} does not appear to be a valid port. Allowed range: 1-65535')


def check_ip(ip):
    return ipaddress.ip_address(ip)


def generate_ws_addr(ip, port):
    check_ip(ip)
    check_port(port)
    return 'ws://' + ip + ':' + str(port)

def get_contracts_data_filepath(skale_env):
    return os.path.join(ENVS_DIR, f'{skale_env.value}.json')

def get_abi(skale_env, abi_filepath=None):
    if (skale_env != BlockchainEnv.CUSTOM):
        abi_filepath = get_contracts_data_filepath(skale_env)
    with open(abi_filepath) as data_file:
        return json.load(data_file)

def generate_nonce():
    return randint(0, 65534)


def random_string(size=6, chars=string.ascii_lowercase):
    return ''.join(random.choice(chars) for x in range(size))


def generate_random_ip():
    return '.'.join('%s' % random.randint(0, 255) for i in range(4))


def generate_random_name(len=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=len))


def generate_random_port():
    return random.randint(0, 60000)

def load_yaml(filepath):
    with open(filepath, 'r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)

def load_skale_env_file():
    return load_yaml(SKALE_ENVS_FILEPATH)

def load_skale_env_config(env):
    env_file = load_skale_env_file()
    return env_file['envs'][env.value]

def generate_custom_config(ip, ws_port):
    if (not ip or not ws_port):
        raise ValueError(
            f'For custom init you should provide ip and ws_port: {ip}, {ws_port}')
    return {
        'ip': ip,
        'ws_port': ws_port,
    }


def send_eth(skale, account, amount, wallet):
    eth_nonce = get_nonce(skale, wallet['address'])
    txn = {
        'to': account,
        'from': wallet['address'],
        'value': amount,
        'gasPrice': skale.web3.eth.gasPrice,
        'gas': 21000,
        'nonce': eth_nonce
    }
    signed_txn = skale.web3.eth.account.signTransaction(txn, private_key=wallet['private_key'])
    tx = skale.web3.eth.sendRawTransaction(signed_txn.rawTransaction)

    logger.info(f'eth sent to {account}, amount: {amount} - transaction_hash: {skale.web3.toHex(tx)}')
    return tx


def private_key_to_public(pr):
    pr_bytes = Web3.toBytes(hexstr=pr)
    pk = keys.PrivateKey(pr_bytes)
    return pk.public_key

def public_key_to_address(pk):
    hash = Web3.sha3(hexstr=str(pk))
    return Web3.toHex(hash[-20:])