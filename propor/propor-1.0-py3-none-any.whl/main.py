from .propor import transfer_file
from pathlib import Path
from sys import argv


def main():
    username = input('username:')
    password = input('password:')
    from_path, host, *to_path = argv
    from_path = Path(from_path).parent
    if not from_path.exists():
        raise FileNotFoundError
    to_path = to_path[0] if to_path else '.'
    transfer_file(host=host, username=username, password=password, from_path=from_path, to_path=to_path)
