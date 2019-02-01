from unittest import TestCase
import unittest

from skale import Skale
import skale.utils.helper as Helper


class HelperTest(TestCase):
    def setUp(self):
        self.skale = Skale('51.0.1.99', 8546)

    def test_port_check(self):
        Helper.check_port(3000)
        self.assertRaises(ValueError, Helper.check_port, 70000)

    def test_ip_check(self):
        Helper.check_ip('12.34.56.78')
        self.assertRaises(ValueError, Helper.check_ip, '299.233.354.643')

    def test_generate_nonce(self):
        nonce = Helper.generate_nonce()
        self.assertTrue(1 <= nonce <= 65534)

    def test_get_abi(self):
        default_abi = Helper.get_abi()
        custom_path = Helper.get_default_abipath()
        custom_path_abi = Helper.get_abi(custom_path)
        self.assertEqual(default_abi, custom_path_abi)


if __name__ == '__main__':
    unittest.main()
