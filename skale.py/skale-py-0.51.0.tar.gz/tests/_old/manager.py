from unittest import TestCase
from skale import Skale, EventListener
import skale
from web3 import Web3
import os, random, unittest, socket
from tests._old.utils import init_logger


class ManagerContractTest(TestCase):
    def setUp(self):
        self.skale = Skale('51.0.1.99', 8546)
        init_logger()

    def run_node_listener(self):
        event = skale.nodes.contract.events.NodeCreated
        listener = EventListener(event, self.node_created_handler, 5)
        listener.run()

    def node_created_handler(self, event):
        ip = socket.inet_ntoa(event['args']['ip'])
        config = {
            'node_id': event['args']['nodeIndex'],
            'owner': event['args']['owner'],
            'port': event['args']['port'],
            'time:': event['args']['time'],
            'ip': ip
        }
        # todo: check configs!

    def test_create_node(self):
        ip = '{}.{}.{}.{}'.format(*random.sample(range(0, 255), 4))
        port = random.randint(0, 65000)

        addr = '0x6870ea70c8582a3c3c778ae719b502e4644fd9de'
        address_fx = Web3.toChecksumAddress(addr)

        wallet = {
            'address': address_fx,
            'private_key': os.environ['ETH_PRIVATE_KEY']
        }

        self.skale.manager().create_node(ip, port, wallet)


    def test_get_node(self):
        node_id = 11 # todo: get node_id from the config
        node = self.skale.manager().get_node(node_id)
        print(node)
        # todo: add check



if __name__ == '__main__':
    unittest.main()
