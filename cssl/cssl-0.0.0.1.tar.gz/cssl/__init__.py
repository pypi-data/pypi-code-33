from string import ascii_lowercase
from itertools import cycle


all_alphabets = ascii_lowercase + ascii_lowercase.upper()


class Cipher(object):
    def __init__(self, message, encryptor, decryptor):
        self.message = message
        self.encrypt = encryptor
        self.decryptor = decryptor


def shift(alphabet, distance):
    is_lower = (ord(alphabet)-97) >= 0
    mod = is_lower*97+(1-is_lower)*65
    return chr((ord(alphabet)%mod+distance)%26+mod)


class Substitution(object):
    def  __init__(self, message=None):
        self.message = message
    def _encrypt_shift(self, dist, message=None):
        if message is None:
            message = self.message
        return ''.join([shift(alph, dist) if alph in all_alphabets else alph for alph in message])
    def _decrypt_shift(self, cipher, shift):
        return self._encrypt_shift(-shift, cipher)
    def substitution(self, dist, message=None):
        if message is None:
            message = self.message
        return Cipher(message, encryptor=lambda msg: self._encrypt_shift(dist, msg), decryptor=self._decrypt_shift)
    def vigenère(self, key, message=None):
        if message is None:
            message = self.message
        return ''.join(zip(cycle(key), message))
        print(pumped_key)
a = Substitution("abcdefghijklmnopqrstuvwxyz")
cipher = a.substitution(12)

print(a.vigenère('le', "abcdefghijklmno"))
