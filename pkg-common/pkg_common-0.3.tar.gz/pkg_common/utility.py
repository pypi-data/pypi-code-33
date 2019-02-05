import os

from cryptography.fernet import Fernet


KEY = b'WV9PaFYoxFoURR9ABpNTxRjuxAtJRx2j1zg_wNqaENY='


def encrypt(info):
    f = Fernet(os.environ.get('KEY_SECRET', KEY))
    return f.encrypt(info.encode())


def decrypt(info):
    f = Fernet(os.environ.get('KEY_SECRET', KEY))
    return f.decrypt(info).decode()