#!/usr/bin/env python
# encoding: utf-8

import requests
import cli_print as cp


def random_an_user(gender: str = 'male', nation: str = 'us'):
    """
    Generate a fake user by https://randomuser.me/
    :param str gender: Gender
    :param str nation: Nation
    :return: dict
    """
    resp = requests.get('https://randomuser.me/api/?gender={gender}&nat={nation}'.format(
        gender=gender, nation=nation
    ))

    return resp.json()['results'][0]


def fake_name(gender: str = 'male', nation: str = 'us', cli: bool = False):
    """
    Get a random user first/last name.

    :param str gender: Gender
    :param str nation: Nation
    :param bool cli:
    :return: str, str
    """
    if cli:
        cp.getting('Random a name')

    r = random_an_user(gender=gender, nation=nation)

    name = r['name']

    first_name = name['first'].strip().capitalize()
    last_name = name['last'].strip().capitalize()

    if cli:
        cp.value('{} {}'.format(first_name, last_name))

    return first_name, last_name
