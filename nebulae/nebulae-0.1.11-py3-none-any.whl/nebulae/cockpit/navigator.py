#!/usr/bin/env python
'''
navigator
Created by Seria at 23/12/2018 11:21 AM
Email: zzqsummerai@yeah.net

                    _ooOoo_
                  o888888888o
                 o88`_ . _`88o
                 (|  0   0  |)
                 O \   。   / O
              _____/`-----‘\_____
            .’   \||  _ _  ||/   `.
            |  _ |||   |   ||| _  |
            |  |  \\       //  |  |
            |  |    \-----/    |  |
             \ .\ ___/- -\___ /. /
         ,--- /   ___\<|>/___   \ ---,
         | |:    \    \ /    /    :| |
         `\--\_    -. ___ .-    _/--/‘
   ===========  \__  NOBUG  __/  ===========
   
'''
# -*- coding:utf-8 -*-
from ..law import Law

class Stage(object):
    START = 'START'
    END = 'END'
    ACCELERATE = 'ACCELERATE'
    FORWARD = 'FORWARD'
    PREFLIGHT = 'PREFLIGHT'
    ANALYZE = 'ANALYZE'
    BREAK_DOWN = 'BREAK_DOWN'
    stages = [START, END, ACCELERATE, FORWARD, PREFLIGHT, ANALYZE, BREAK_DOWN]
    phases = [[ACCELERATE], [FORWARD]]

    @classmethod
    def register(cls, stage, group):
        stage = stage.upper()
        if stage in cls.stages:
            raise Exception('%s is an existing component in warehouse.' % stage)
        exec('Stage.%s = "%s"' % (stage, stage))
        cls.stages.append(stage)
        if group.upper() in ['ACCELERATE', 'A']:
            cls.phases[0].append(stage)
        elif group.upper() in ['FORWARD', 'F']:
            cls.phases[-1].append(stage)
        else:
            raise KeyError('There is no group named %s.' % group)



def Navigator(dashboard, time_machine, fuel_depot, spacecraft):
    core = Law.CORE.upper()
    if core == 'TENSORFLOW':
        from .navigator_tf import NavigatorTF
        return NavigatorTF(dashboard, time_machine, fuel_depot, spacecraft)
    else:
        raise ValueError('%s has not been a supported core.' % core)