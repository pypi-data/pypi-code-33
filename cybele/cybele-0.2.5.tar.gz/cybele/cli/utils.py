import json
import os
import sys

import click
from terminaltables import SingleTable

from ..aes import AESCipher, passphrase_to_key
from ..api import Database


class Table(SingleTable):
    def __init__(self, data, **kwargs):
        SingleTable.__init__(self, data)
        for attr, value in kwargs.items():
            if not hasattr(self, attr):
                raise AttributeError(f"Table has no '{attr}' attribute")
            setattr(self, attr, value)

    def __str__(self):
        return str(self.table)


def load_db(db_path):
    key = passphrase_to_key(ask_passphrase())
    db = Database(db_path, key)
    return db


def confirm_yes_no(msg):
    choice = click.prompt(f"{msg} (yes/no)")
    if choice not in ["y", "n", "yes", "no"]:
        choice = confirm_yes_no(msg)
    if choice in ["n", "no"]:
        return False
    if choice in ["y", "yes"]:
        return True


def echo_exit(msg, exit_code=1):
    click.echo(msg)
    sys.exit(exit_code)


def ask_passphrase():
    return click.prompt("Enter passphrase", hide_input=True)


def ask_full_infos():
    username = ask_username()
    passphrase = ask_and_confirm_passphrase()
    return {"username": username, "passphrase": passphrase}


def ask_username():
    return click.prompt("Username")


def ask_and_confirm_passphrase():
    passphrase = click.prompt("Enter passphrase", hide_input=True)
    confirmation = click.prompt("Enter same passphrase again", hide_input=True)
    if passphrase != confirmation:
        echo_exit("Passphrases do not match. Try again")
    return passphrase


def create_db(db_path):
    db_dir, db_name = os.path.split(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    if os.path.exists(db_path):
        echo_exit(f"DB {db_path} already exists.")

    passphrase = ask_and_confirm_passphrase()
    key = passphrase_to_key(passphrase)
    cipher = AESCipher(key)
    with open(db_path, "w") as f:
        dumps = json.dumps({})
        f.write(cipher.encrypt(dumps))
