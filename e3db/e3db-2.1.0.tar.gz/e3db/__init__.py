import os
from .config import Config
from .client import Client
if 'CRYPTO_SUITE' in os.environ and os.environ['CRYPTO_SUITE'] == 'NIST':
    from .nist_crypto import NistCrypto as Crypto
else:
    from .sodium_crypto import SodiumCrypto as Crypto
from .exceptions import APIError, QueryError, LookupError, ConflictError, CryptoError
