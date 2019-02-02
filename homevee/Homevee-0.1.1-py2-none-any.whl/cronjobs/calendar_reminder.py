#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
from time import sleep

from homevee.db_utils import get_database_con


def remind_users():
    db = get_database_con()

    with db:
        #query events and remind users of upcoming calendar entries

        return


def init_thread():
    #wait until midnight + 5 minutes
    t = datetime.datetime.today()

    remind_users()

    sleep(60)