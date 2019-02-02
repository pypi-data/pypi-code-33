#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

END_OF_MESSAGE = "[END_OF_MESSAGE]"

HOMEVEE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(HOMEVEE_DIR, 'data')

SSL_FULLCHAIN = os.path.join(HOMEVEE_DIR, 'fullchain.pem')
SSL_CERT = os.path.join(HOMEVEE_DIR, 'cert.pem')

LOCAL_SSL_PRIVKEY = os.path.join(HOMEVEE_DIR, 'local_privkey.pem')
LOCAL_SSL_CERT = os.path.join(HOMEVEE_DIR, 'local_cert.pem')