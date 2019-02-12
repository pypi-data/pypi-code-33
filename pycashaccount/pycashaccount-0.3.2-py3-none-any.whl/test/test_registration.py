import unittest
from unittest import mock

import cashaccount.payment as pay
import cashaccount.registration as rgstr


class TestNameValidation(unittest.TestCase):
    MAX_NAME_LENGTH = 99

    def test_allows_valid_names(self):
        rgstr.validate_name('lower')
        rgstr.validate_name('UPPER')
        rgstr.validate_name('mixedCASE')
        rgstr.validate_name('mixedWITH01234')
        rgstr.validate_name('mixedWITH__01234')
        rgstr.validate_name('a' * self.MAX_NAME_LENGTH)

    def test_raises_ValueError_for_invalid_names(self):
        invalid_names = (
            'nonalphabet文字',
            'hyphens-not-allowed',
            'a' * (self.MAX_NAME_LENGTH + 1),
        )
        for invalid_name in invalid_names:
            with self.assertRaises(ValueError):
                rgstr.validate_name(invalid_name)


class TestConverters(unittest.TestCase):
    STR = 'emergent_reasons'
    UTF8HEX = '656d657267656e745f726561736f6e73'

    def test_str_to_utf8hex(self):
        self.assertEqual(rgstr.str_to_utf8hex(self.STR), self.UTF8HEX)

    def test_utf8hex_to_str(self):
        self.assertEqual(rgstr.utf8hex_to_str(self.UTF8HEX), self.STR)


class TestOpPush(unittest.TestCase):
    def test_minpush_works_for_short_data(self):
        self.assertEqual(rgstr._minpush_for('00' * 1), '01')  # minimum push
        self.assertEqual(rgstr._minpush_for('00' * 9), '09')
        self.assertEqual(rgstr._minpush_for('00' * 30), '1e')
        self.assertEqual(rgstr._minpush_for('00' * 75), '4b')  # max specific push code

    def test_minpush_works_for_var_data(self):
        self.assertEqual(rgstr._minpush_for('00' * 76), '764c')  # min push 1 byte
        self.assertEqual(rgstr._minpush_for('00' * (2**8-1)), '76ff')  # max push 1 byte

    def test_minpush_raises_exception_for_invalid_lengths(self):
        with self.assertRaises(Exception):
            rgstr._minpush_for('')
        with self.assertRaises(Exception):
            too_many_bytes = '00' * 2**8
            rgstr._minpush_for(too_many_bytes)
        with self.assertRaises(Exception):
            odd_number_of_nibbles = '0' * 3
            rgstr._minpush_for(odd_number_of_nibbles)


class TestTxOutputs(unittest.TestCase):
    def setUp(self):
        name = 'emergent_reasons'
        payment_info = pay.KeyHashInfo('bitcoincash:qrme8l598x49gmjhn92dgwhk5a3znu5wfcf5uf94e9')
        self.registration = rgstr.Registration(name, payment_info)

    def test_electron_markdown_with_key_hash(self):
        expected = ('<push><hex>01010101'
                    '<push><hex>656d657267656e745f726561736f6e73'
                    '<push><hex>01f793fe8539aa546e579954d43af6a76229f28e4e')

        self.assertEqual(rgstr.electron_markdown(self.registration), expected)

    def test_opreturn_hex_with_key_hash(self):
        expected = ''.join([
            '04',                                         # OP_RETURN
            '01010101',                                   # cash account protocol
            '10',                                         # push x bytes of name
            '656d657267656e745f726561736f6e73',           # name
            '15',                                         # push 0x15 (21) bytes of payment info
            '01f793fe8539aa546e579954d43af6a76229f28e4e'  # 01 payment type + info
        ])
        self.assertEqual(rgstr.opreturn(self.registration), expected)


class TestString(unittest.TestCase):
    def test_has_useful_info(self):
        expected = ('name:      emergent_reasons\n'
                    'op_return: ffffffff\n'
                    'payment info:\n'
                    '  some lines\n'
                    '  of payment info')

        m_payment_info = mock.MagicMock()
        m_payment_info.__str__.return_value = 'some lines\nof payment info'

        with mock.patch('cashaccount.registration.opreturn', return_value='ffffffff'):
            result = str(rgstr.Registration('emergent_reasons', m_payment_info))
        self.assertEqual(result, expected)
