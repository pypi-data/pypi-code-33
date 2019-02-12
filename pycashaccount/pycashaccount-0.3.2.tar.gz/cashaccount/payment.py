import base58

import cashaddress


class _Info:
    TYPE_BYTE = None  # override with fixed value
    NAME = None       # override with fixed value

    def base(self):
        """Return a human string for sites like cashaccount.info"""
        raise NotImplementedError

    def _data_hex(self):
        """Return the data payload of the cash account hex."""
        raise NotImplementedError

    def cashaccount_hex(self):
        """Return the full payment info string as <Payment Type + Payment Data>."""
        return '{:02x}{}'.format(self.TYPE_BYTE, self._data_hex().lower())

    def __str__(self):
        return ('{}\n'
                'base:            {}\n'
                'cashaccount hex: {}'.format(self.NAME, self.base(), self.cashaccount_hex()))


class KeyHashInfo(_Info):
    """Key Hash data is the 20 byte hash160 address data (no version prefix, no checksum suffix)."""
    TYPE_BYTE = 0x01
    NAME = 'Key Hash (P2PKH) Info'

    def __init__(self, address_string):
        address = _normalize(address_string)
        self._validate_version(address.version)
        self._address = address
        self._hash160_hex = _extract_hash160(address)

    def base(self):
        return self._address.cash_address()

    def _data_hex(self):
        return self._hash160_hex

    @staticmethod
    def _validate_version(v):
        if not v.startswith('P2PKH'):
            raise ValueError('expected a P2PKH address but got {}'.format(v))


class ScriptHashInfo(KeyHashInfo):
    TYPE_BYTE = 0x02
    NAME = 'Script Hash (P2SH) Info'

    @staticmethod
    def _validate_version(v):
        if not v.startswith('P2SH'):
            raise ValueError('expected a P2SH address but got {}'.format(v))


class PaymentCodeInfo(_Info):
    TYPE_BYTE = 0x03
    NAME = 'Payment Code (Bip47) Info'

    def __init__(self, payment_code):
        self._validate_paymentcode(payment_code)
        self._payment_code = payment_code
        # take all payment code data bytes except for the version byte
        self._paymentcode_payload = base58.b58decode_check(self._payment_code)[1:].hex()

    def base(self):
        return self._payment_code

    def _data_hex(self):
        return self._paymentcode_payload

    @classmethod
    def from_xpub(cls, xpub):
        cls._validate_xpub(xpub)
        xpub_decoded_bytes = base58.b58decode_check(xpub)
        pubkey_bytes = xpub_decoded_bytes[45:78]
        chaincode_bytes = xpub_decoded_bytes[13:45]
        payment_code_data = bytes([
            # 47 lets anyone looking at this data know that this is for bip47
            # but it is not used until base58 encoding and not part of the fixed payment code data
            0x47,
            # 1 is the payment code version. There is also version 2 with different data
            0x01,
            # 0 shows that we are not using "bitmessage" for notifications.
            0x00,
            # next we unpack the 33-byte compressed public key with a "*".
            *pubkey_bytes,
            # then we unpack the 32-byte chain code
            *chaincode_bytes,
            # then we dump 13 bytes of zero in the space reserved for future features
            *[0x00] * 13
        ])
        payment_code = base58.b58encode_check(payment_code_data).decode('utf-8')
        return cls(payment_code)

    @staticmethod
    def _validate_paymentcode(pc_string):
        try:
            payload = base58.b58decode_check(pc_string)
        except ValueError as e:
            raise ValueError('unable to interpret payment code: {}'.format(e))

        version_byte = payload[0]
        if version_byte != 0x47:
            raise ValueError('expected payment code payload to start with 0x47 but got {:02x}'
                             ''.format(version_byte))

    @staticmethod
    def _validate_xpub(xpub_string):
        prefix = xpub_string[:4]
        if prefix not in ['xpub', 'tpub']:
            raise ValueError('expected xpub to start with "xpub" or "tpub" but found {}'.format(prefix))

        try:
            base58.b58decode_check(xpub_string)
        except ValueError as e:
            raise ValueError('unable to interpret xpub: {}'.format(e))


def _normalize(address_string):
    """Convert legacy or cashaddr string to an address object.

    Raises ValueError for invalid address strings.
    """
    if _looks_like_cashaddr_without_prefix(address_string):
        address_string = 'bitcoincash:{}'.format(address_string)

    # get an address object that is independent of the input format
    try:
        return cashaddress.convert.Address.from_string(address_string)
    except cashaddress.convert.InvalidAddress as e:
        raise ValueError('unable to interpret address: {}'.format(e))


def _looks_like_cashaddr_without_prefix(s):
    if s[0] not in ['p', 'q']:
        return False
    return True


def _extract_hash160(address):
    no_checksum = base58.b58decode_check(address.legacy_address())
    no_version_no_checksum = no_checksum[1:]
    return no_version_no_checksum.hex()
