#!/usr/bin/env python
'''Python script to run `fluidmirror sync` intermittently

Usage
-----
nohup python -u mirror_launch.py > ~/.fluiddyn/mirror.log 2>&1 &

'''
from __future__ import print_function

import sched
import time
from datetime import datetime
from random import random
from fluiddevops.mirror import main


s = sched.scheduler(time.time, time.sleep)
every = 3 * 60 * 60  # seconds


def job():
    rnd_max = every * 0.1
    rnd_delay = 2 * (random() - 0.5) * rnd_max
    print(
        'fluidmirror sync run once in {} and run every {} +/- {} seconds'.format(
            rnd_delay, every, rnd_max))
    s.enter(rnd_delay * 1, 1, main, [['sync']])
    s.enter(rnd_delay * 2, 1, main, [['sync', '-b', 'dev']])
    while True:
        print('Time: ', datetime.fromtimestamp(time.time()))
        rnd_delay = 2 * (random() - 0.5) * rnd_max
        s.enter(every + rnd_delay * 1, 1, main, [['sync']])
        s.enter(every + rnd_delay * 2, 1, main, [['sync', '-b', 'dev']])
        s.run()


if __name__ == '__main__':
    job()
