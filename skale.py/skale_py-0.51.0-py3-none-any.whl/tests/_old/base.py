from unittest import TestCase
from skale import Skale, Manager, Token, BaseContract
import unittest


class Web3Test(TestCase):
    def setUp(self):
        self.skale = Skale('51.0.1.99', 8546)

    def test_connection(self):
        self.assertTrue(self.skale.web3.isConnected(), 'not connected to node')

    def test_contracts_instances(self):
        self.assertIsInstance(self.skale.manager, Manager)
        self.assertIsInstance(self.skale.token, Token)

        self.assertIsInstance(self.skale.manager, BaseContract)
        self.assertIsInstance(self.skale.token, BaseContract)


if __name__ == '__main__':
    unittest.main()
