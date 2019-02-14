from .base_crypto import BaseCrypto
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


class NistCrypto(BaseCrypto):

    @classmethod
    def get_mode(self):
        return 'nist'

    @classmethod
    def encrypt_secret(self, ak, plain, nonce):
        # Prepend the nonce to the encrypted value for parity with the Sodium implementation
        return nonce + AESGCM(ak).encrypt(nonce, plain, None)

    @classmethod
    def decrypt_secret(self, ak, ciphertext, nonce):
        return AESGCM(ak).decrypt(nonce, ciphertext, None)

    @classmethod
    def encrypt_ak(self, private_key, public_key, ak, nonce):
        # Prepend the nonce to the encrypted value for parity with the Sodium implementation
        return nonce + self._exchange(private_key, public_key).encrypt(nonce, ak, None)

    @classmethod
    def decrypt_eak(self, private_key, public_key, eak, nonce):
        return self._exchange(private_key, public_key).decrypt(nonce, eak, None)

    @classmethod
    def _exchange(self, private_key, public_key):
        shared = private_key.exchange(ec.ECDH(), public_key)
        derived = HKDF(
            algorithm=hashes.SHA384(),
            length=32,
            salt=None,
            info=None,
            backend=default_backend()
        ).derive(shared)
        return AESGCM(derived)

    @classmethod
    def decode_public_key(self, key):
        serialized = BaseCrypto.base64decode(key)
        return serialization.load_pem_public_key(
            data=serialized,
            backend=default_backend()
        )

    @classmethod
    def encode_public_key(self, key):
        serialized = key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return BaseCrypto.base64encode(serialized)

    @classmethod
    def decode_private_key(self, key):
        serialized = BaseCrypto.base64decode(key)
        return serialization.load_pem_private_key(
            data=serialized,
            password=None,
            backend=default_backend()
        )

    @classmethod
    def encode_private_key(self, key):
        serialized = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return BaseCrypto.base64encode(serialized)

    @classmethod
    def random_key(self):
        return AESGCM.generate_key(bit_length=256)

    @classmethod
    def random_nonce(self):
        return os.urandom(12)

    @classmethod
    def generate_keypair(self):
        private_key = ec.generate_private_key(
            ec.SECP384R1(), default_backend()
        )
        public_key = private_key.public_key()

        return public_key, private_key
