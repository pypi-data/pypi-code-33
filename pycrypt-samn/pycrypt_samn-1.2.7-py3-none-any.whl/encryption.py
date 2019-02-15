
import os
import platform
import base64
import hashlib
import random
from pycrypt.pkcs7 import PKCS7Encoder
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP


# MUST USE PYTHON 3.5+

def _get_random_unicode(length):

    try:
        get_char = unichr
    except NameError:
        get_char = chr

    # Update this to include code point ranges to be sampled
    include_ranges = [
        ( 0x0021, 0x0021 ),
        ( 0x0023, 0x0026 ),
        ( 0x0028, 0x007E ),
        ( 0x00A1, 0x00AC ),
        ( 0x00AE, 0x00FF ),
        ( 0x0100, 0x017F ),
        ( 0x0180, 0x024F ),
        ( 0x2C60, 0x2C7F ),
        ( 0x16A0, 0x16F0 ),
        ( 0x0370, 0x0377 ),
        ( 0x037A, 0x037E ),
        ( 0x0384, 0x038A ),
        ( 0x038C, 0x038C ),
    ]

    alphabet = [
        get_char(code_point) for current_range in include_ranges
            for code_point in range(current_range[0], current_range[1] + 1)
    ]
    return ''.join(random.choice(alphabet) for i in range(length))


class MD5:

    def __init__(self, hxstr, btstr):
        self.HexString = hxstr
        self.ByteString = btstr


class AESCipher(object):
    """
        Custom class for creating a AES Cipher for encryption/decryption processing
        By default this uses AES Cipher Mode CFB. this is built for specific purpose and not
        designed to be used with all AES Cipher Modes.
    """
    def __init__(self):
        self.AES_BLOCK_SIZE = AES.block_size
        self.AES_KEY = Random.get_random_bytes(32)
        self.padding = PKCS7Encoder()
        self.decrypted_bytes = None
        self.decrypted_data = None

    def encrypt(self, raw, *args, **kwargs):
        if isinstance(raw, str):
            tmp = self.padding.encode(raw).encode('utf')
        else:
            raise ValueError("data to be encrypted is not in 'str' form")

        kwargs['iv'] = Random.get_random_bytes(self.AES_BLOCK_SIZE)
        cipher = AES.new(key=self.AES_KEY,
                         mode=AES.MODE_CFB,
                         *args,
                         **kwargs)
        ciphertext = cipher.encrypt(tmp)
        return base64.b64encode(kwargs['iv'] + ciphertext)

    def decrypt(self, enc, key, *args, **kwargs):
        if key:
            if isinstance(key, str):
                self.AES_KEY = base64.b64decode(key)
            else:
                self.AES_KEY = key
        enc = base64.b64decode(enc)
        kwargs['iv'] = enc[:self.AES_BLOCK_SIZE]
        cipher = AES.new(self.AES_KEY, AES.MODE_CFB, *args, **kwargs)
        self.decrypted_bytes = cipher.decrypt(enc[self.AES_BLOCK_SIZE:])
        ciphertext = self.padding.get_text(self.decrypted_bytes)
        return self.padding.decode(ciphertext)


class Encryption(object):
    """
    This class does the heavy lifting of encrypting string, decrypting strings, generating
    RSA Key-pair, or pulling the MD5 hash of a file. There is a default secret_code,
    but shouldn't have to tell you ... never use the default outside of development.
    """

    def __init__(self):
        self.__encrypted_message = None
        self.__decrypted_message = None

    def encrypt(self, privateData, publickey_file, output_file=None):

        if type(privateData) is str:
            privateData = privateData.encode("utf-8")

        pubkey = RSA.import_key(open(publickey_file, 'r').read())
        cipher_rsa = PKCS1_OAEP.new(pubkey)
        encrypted_message = cipher_rsa.encrypt(privateData)

        self.__decrypted_message = None
        self.__encrypted_message = base64.b64encode(encrypted_message)
        if output_file:
            with open(output_file, 'wb') as f:
                f.write(self.__encrypted_message)
                f.close

    def get_encrypted_message(self):
        return self.__encrypted_message

    def decrypt(self, encrypted_data, private_key_file, secret_code=None):

        if os.path.isfile(encrypted_data):
            with open(encrypted_data, 'rb') as f:
                encrypted_data = f.read()
                f.close()
        if isinstance(secret_code, str):
            # encode this to a bytes object
            secret_code = secret_code.encode('utf-8')

        if secret_code:
            private_key = RSA.import_key(open(private_key_file, 'rb').read(), passphrase=secret_code)
        else:
            private_key = RSA.import_key(open(private_key_file, 'rb').read())

        encrypted_data = base64.b64decode(encrypted_data)
        cipher_rsa = PKCS1_OAEP.new(private_key)
        privateData = cipher_rsa.decrypt(encrypted_data)

        self.__decrypted_message = privateData
        self.__encrypted_message = None

    def get_decrypted_message(self):
        try:
            utf_str = str(self.__decrypted_message, 'utf-8')
            return utf_str
        except UnicodeDecodeError:
            return self.__decrypted_message

    def generate_rsa_key_pair(self, public_file=None, private_file=None,
                              secret_code=b'N-6NZG\xff<\xddL\x85:\xc5\xc4\xa8n'):

        key = RSA.generate(4096)

        private, public = key.exportKey(passphrase=secret_code, pkcs=8,
                                        protection="scryptAndAES256-CBC"), key.publickey().exportKey()

        with open(private_file, 'wb') as f:
            f.write(private)
            f.close
        with open(public_file, 'wb') as f:
            f.write(public)
            f.close

        setattr(self, 'PublicKey_file', public_file)
        setattr(self, 'PrivateKey_file', private_file)

        return self

    def get_rsa_public_key_from_private_key(self, file_path=None, encrypted_key=None,
                                            secret_code=b'N-6NZG\xff<\xddL\x85:\xc5\xc4\xa8n'):

        if file_path:
            encrypted_key = open(file_path, 'rb').read()

        key = RSA.import_key(encrypted_key, passphrase=secret_code)

        setattr(self, 'PublicKey', key.publickey().exportKey())

        return self

    def md5(self, fname):
        import hashlib

        hash_md5 = hashlib.md5()

        with open(fname, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
            f.close()
        setattr(self, 'md5_info', MD5(hash_md5.hexdigest(), hash_md5.digest()))
        return self.md5_info
