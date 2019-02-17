import base64
import hashlib
import os

from Crypto.Cipher import AES


def passphrase_to_key(passphrase):
    return hashlib.sha256(passphrase.encode("utf8")).digest()


class AESCipher(object):
    def __init__(self, key):
        self.iv_size = 16
        self.key = key

    def encrypt(self, plaintext):
        plaintext = self._pad(plaintext)
        iv = os.urandom(self.iv_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(plaintext)
        return base64.b64encode(iv + encrypted).decode('utf8')

    def decrypt(self, encrypted):
        encrypted = base64.b64decode(encrypted.encode('utf8'))
        iv, encrypted = encrypted[:self.iv_size], encrypted[self.iv_size:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(encrypted)).decode('utf8')

    def _pad(self, s):
        s = s.encode('utf8')
        return s + (self.iv_size - len(s) % self.iv_size) * chr(self.iv_size - len(s) % self.iv_size).encode('utf8')

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]
