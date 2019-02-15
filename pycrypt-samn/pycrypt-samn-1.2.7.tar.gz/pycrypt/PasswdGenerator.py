
import string
import random
from .encryption import Encryption


class PasswordGenerator:

    CHARS = chars = string.ascii_letters + string.digits + string.punctuation
    ALPHANUMERIC = string.ascii_letters + string.digits

    def __init__(self):
        self.pw_size = 8
        self.__passwd = ''

        # going to exclude the quotes from password generator to prevent any potential issues
        self.excluded_chars = []

    def generate(self, size=8, excluded_chars=[], encrypt=False,
                 public_key='/u01/prd/rsa/local_pub', output_file=None, AlphaNumeric=False):
        self.pw_size = size
        self.excluded_chars += excluded_chars
        while len(self.__passwd) < self.pw_size:
            if AlphaNumeric:
                c = random.choice(self.ALPHANUMERIC)
            else:
                c = random.choice(self.CHARS)
            if not self.excluded_chars.__contains__(c):
                self.__passwd += ''.join(c)
        self.__dpasswd = self.__passwd
        if encrypt:
            enc = Encryption()

            if output_file:
                enc.encrypt(publickey_file=public_key,
                            privateData=self.__passwd,
                            output_file=output_file)
            else:
                enc.encrypt(publickey_file=public_key,
                            privateData=self.__passwd)
            self.__passwd = enc.get_encrypted_message()

    def print(self):
        print(self.__passwd)

    def get(self):
        return self.__passwd

    def get_decrypted(self):
        return self.__dpasswd
