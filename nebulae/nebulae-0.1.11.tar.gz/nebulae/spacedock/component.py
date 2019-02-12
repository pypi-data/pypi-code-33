#!/usr/bin/env python
'''
component
Created by Seria at 25/11/2018 2:58 PM
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
from copy import deepcopy
from ..law import Law

class Pod:
    def __init__(self, comp, symbol, name, msg=[]):
        self.component = comp
        self.symbol = symbol
        self.message = msg
        self.name = name

    def __rshift__(self, other):
        return Pod([self, other], '>', 'CASCADE')

    def __add__(self, other):
        return Pod([self, other], '+', 'ADD')

    def __sub__(self, other):
        return Pod([self, other], '-', 'SUB')

    def __mul__(self, other):
        return Pod([self, other], '*', 'MUL')

    def __matmul__(self, other):
        return Pod([self, other], '@', 'MATMUL')

    def __and__(self, other):
        return Pod([self, other], '&', 'CONCAT')

    def __pow__(self, power, modulo=None):
        assert isinstance(power, int)
        pod = deepcopy(self)
        pod._appendSerialNo('0')
        for p in range(1, power):
            pod_temp = deepcopy(self)
            pod_temp._appendSerialNo(str(p))
            pod = pod >> pod_temp
        return pod

    def _appendSerialNo(self, serial_no):
        if isinstance(self.component, list):
            self.component[0]._appendSerialNo(serial_no)
            self.component[1]._appendSerialNo(serial_no)
        else:
            self.name += '_' + serial_no

    def show(self):
        if isinstance(self.component, list):
            self.component[0].show()
            self.component[1].show()
        else:
            print(self.name)



def Component():
    core = Law.CORE.upper()
    if core == 'TENSORFLOW':
        from .component_tf import ComponentTF
        return ComponentTF()
    else:
        raise ValueError('%s has not been a supported core.' % core)