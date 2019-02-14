import base64


class BaseCrypto:

    @classmethod
    def get_mode(self):
        pass

    @classmethod
    def encrypt_secret(self, ak, plain, nonce):
        pass

    @classmethod
    def decrypt_secret(self, ak, ciphertext, nonce):
        pass

    @classmethod
    def encrypt_ak(self, private_key, public_key, ak, nonce):
        pass

    @classmethod
    def decrypt_eak(self, private_key, public_key, eak, nonce):
        pass

    @classmethod
    def decode_public_key(self, key):
        pass

    @classmethod
    def encode_public_key(self, key):
        pass

    @classmethod
    def decode_private_key(self, key):
        pass

    @classmethod
    def encode_private_key(self, key):
        pass

    @classmethod
    def random_key(self):
        pass

    @classmethod
    def random_nonce(self):
        pass

    @classmethod
    def generate_keypair(self):
        # return public, private
        pass

    @staticmethod
    def to_bytes(b):
        if type(b) is bytes:
            return b
        elif type(b) is str:
            return bytes(b, "utf-8")
        else:
            return bytes(b)

    @classmethod
    def base64decode(self, s):
        # From https://stackoverflow.com/a/9956217
        # Python base64 implementation requires padding, which may not be present in the
        # encoded public/private keypair
        b = BaseCrypto.to_bytes(s)
        return base64.urlsafe_b64decode(b + b'=' * (4 - len(s) % 4))

    @classmethod
    def base64encode(self, s):
        # Encodes a utf-8/ascii bytes into  base 64 encoded bytes
        # remove "=" padding for general SDK compatibility
        b = BaseCrypto.to_bytes(s)
        return base64.urlsafe_b64encode(b).strip(b'=')

    @classmethod
    def encrypt_file(self, plaintext_file, key):
        pass

    @classmethod
    def decrypt_file(self, encrypted_file, destination_file, key):
        pass
