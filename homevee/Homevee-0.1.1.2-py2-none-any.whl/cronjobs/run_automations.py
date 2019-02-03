#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import json
from time import sleep

from homevee.Functions.condition_actions.actions import run_actions
from homevee.Functions.condition_actions.conditions import conditions_true
from homevee.db_utils import get_database_con


def run_trigger_automation(trigger_type, type, id, value, db):
    return

def run_timed_automations():
    #print "running automations"
    db = get_database_con()
    with db:
        cur = db.cursor()

        today = datetime.datetime.today()

        hour = today.hour
        minute = today.minute

        hour_string = str(hour)
        if(hour < 10):
            hour_string = "0"+hour_string

        minute_string = str(minute)
        if(minute < 10):
            minute_string = "0"+minute_string

        time_string = hour_string+":"+minute_string

        #print time_string

        cur.execute('SELECT * FROM AUTOMATION_DATA, AUTOMATION_TRIGGER_DATA WHERE AUTOMATION_DATA.ID = AUTOMATION_RULE_ID AND TYPE = "time" AND IS_ACTIVE = "true" AND VALUE = :val',
                    {'val': time_string})

        automations = cur.fetchall()

        run_automations(automations, db)


    return

def run_automations(automations, db):
    for item in automations:
        print item
        if (conditions_true(json.loads(item['CONDITION_DATA']), db)):
            if (int(item['TRIGGERED']) == 0):
                print "running item: "+str(item)
                run_actions(json.loads(item['ACTION_DATA']), db)
                set_triggered(item['ID'], 1, db)
        else:
            set_triggered(item['ID'], 0, db)

def set_triggered(id, triggered, db):
    with db:
        cur = db.cursor()

        cur.execute("UPDATE AUTOMATION_DATA SET TRIGGERED = :triggered WHERE ID = :id",
                    {'triggered': triggered, 'id': id})



def init_thread():
    #check = check_single_condition({'action': 'weekdays', 'days':[0]}, None)

    #if(check):
    #    print 'true'
    #else:
    #    print 'false'

    while(True):
        run_timed_automations()
        #print "waiting 1 minute"
        sleep(60)