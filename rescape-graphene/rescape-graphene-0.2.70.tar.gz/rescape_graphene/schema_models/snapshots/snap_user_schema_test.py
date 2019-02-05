# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['UserTypeCase::test_create 1'] = {
    'email': '',
    'firstName': 'T',
    'id': '3',
    'isActive': True,
    'isStaff': False,
    'isSuperuser': False,
    'lastName': 'Rex',
    'password': 'pbkdf2_sha256$100000$not_random$4HHNXbLL1N0D4FgkwM5xhtJfUAlK9XVQgx3rIqTT628=',
    'username': 'dino'
}

snapshots['UserTypeCase::test_query 1'] = [
    {
        'email': '',
        'firstName': 'Simba',
        'id': '1',
        'isActive': True,
        'isStaff': False,
        'isSuperuser': False,
        'lastName': 'The Lion',
        'password': 'pbkdf2_sha256$100000$not_random$OGp+DSsDR/iL1G/SAxYQjNWcG6XEY6D1Qayrhj43CDQ=',
        'username': 'lion'
    },
    {
        'email': '',
        'firstName': 'Felix',
        'id': '2',
        'isActive': True,
        'isStaff': False,
        'isSuperuser': False,
        'lastName': 'The Cat',
        'password': 'pbkdf2_sha256$100000$not_random$GqcNMeWDYEwJwwQtye8LxhaTFjwA0z4iJcccDOlZYlg=',
        'username': 'cat'
    },
    {
        'email': '',
        'firstName': 'T',
        'id': '3',
        'isActive': True,
        'isStaff': False,
        'isSuperuser': False,
        'lastName': 'Rex',
        'password': 'pbkdf2_sha256$100000$not_random$4HHNXbLL1N0D4FgkwM5xhtJfUAlK9XVQgx3rIqTT628=',
        'username': 'dino'
    }
]

snapshots['UserTypeCase::test_update 1'] = {
    'email': '',
    'firstName': 'Al',
    'id': '3',
    'isActive': True,
    'isStaff': False,
    'isSuperuser': False,
    'lastName': 'Lissaurus',
    'password': 'pbkdf2_sha256$100000$not_random$4HHNXbLL1N0D4FgkwM5xhtJfUAlK9XVQgx3rIqTT628=',
    'username': 'dino'
}
