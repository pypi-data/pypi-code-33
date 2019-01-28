from string import ascii_lowercase
from itertools import cycle


all_alphabets = ascii_lowercase + ascii_lowercase.upper()


class Cipher(object):
    def __init__(self, encryptor, decryptor):
        self.encrypt = encryptor
        self.decrypt = decryptor


def shift(alphabet, distance):
    is_lower = (ord(alphabet)-97) >= 0
    mod = is_lower*97+(1-is_lower)*65
    return chr((ord(alphabet)%mod+distance)%26+mod)


class Substitution(object):
    def _encrypt_shift(self, dist, message):
        return ''.join([shift(alph, dist) if alph in all_alphabets else alph for alph in message])
    def _decrypt_shift(self, shift, cipher):
        return self._encrypt_shift(-shift, cipher)
    def substitution(self, dist):
        return Cipher(encryptor=lambda msg: self._encrypt_shift(dist, msg), decryptor=lambda msg: self._decrypt_shift(dist, msg))
    
    def vigenère(self, key):
        return Cipher(encryptor=lambda msg: self._encrypt_vigenère(key, msg), decryptor=lambda msg: self._decrypt_vigenère(key, msg))
    def _encrypt_vigenère(self, key, message):
        return ''.join((shift(s1, ord(s2)) for s1, s2 in zip(cycle(key), message)))
    def _decrypt_vigenère(self, key, cipher):
        return ''.join((shift(s2, -ord(s1)) for s1, s2 in zip(cycle(key), cipher)))







