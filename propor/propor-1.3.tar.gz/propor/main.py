from .propor import transfer_file
from pathlib import Path
from os import getcwd
from sys import argv


def main():
    _, host, *to_path = argv
    from_path = Path(getcwd())
    if not from_path.exists():
        raise FileNotFoundError
    to_path = to_path[0] if to_path else '.'
    username = input('username: ')
    password = input('password: ')
    transfer_file(host=host, username=username, password=password, from_path=from_path, to_path=to_path)
    print('Successful!')
