#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib

from Manager.gateway import get_gateway
from gateway_keys import RADEMACHER_HOMEPILOT


def set_modes(id, mode, db):
    data = get_gateway(RADEMACHER_HOMEPILOT, db)
    ip = data['IP']

    url = "http://" + ip + "/deviceajax.do?cid=9&did=10001&goto=" + str(goto) + "&command=0"

    response = urllib.urlopen(url).read()