#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2014年7月22日

@author: zhouzhichao
'''

from polynome import Polynome 

class GaloisField(object):
    '''
            伽罗华有限域
    '''
    def __init__(self, bottom=2, exp=8, gen=2, module=2):
        self.__gfBound = bottom**exp
        self.__gfMaximum = self.__gfBound - 1
        self.__ord2val = {}
        self.__val2ord = {}
        assert gen < self.__gfBound
        if module > 2:
            self.generate(gen, module)
        else:
            self.__gfGen = gen
            self.__gfModule = module
    def generate(self, gen, module):
        self.__gfGen = gen % self.__gfBound
        self.__gfModule = module
        a, c = Polynome(value=gen), Polynome(value=gen)
        m = Polynome(value=module)
        a2n, uniq = {0:1}, set([1])        
        order = 0
        while order < len(uniq) and len(a2n) < self.__gfMaximum:
            order = (order + 1) % self.__gfMaximum
            a2n[order] = val = c.value
            c = a.mul(c).mod(m)
            uniq.add(val)
        self.__gfMaximum = len(uniq-set([0]))
        n2a = {v:k for k, v in a2n.items()}
        if n2a.get(self.__gfMaximum): 
            n2a[0] = n2a[self.__gfMaximum]
            #a2n[n2a[0]] = 0
        self.__ord2val = tuple(map(lambda x:a2n[x], xrange(len(a2n))))
        self.__val2ord = n2a

        return self
    def getOrder(self, value):
        return self.__val2ord.get(value%self.__gfBound)
    def getValue(self, order):
        return self.__ord2val[order%self.__gfMaximum]
    def mod(self, value):
        return value % self.__gfMaximum
    def mul(self, a, b):
        '''
            伽罗华有限域内乘法
            a, b须为int
        '''
        if a==0 or b==0: 
            return 0
        oa, ob = self.getOrder(a), self.getOrder(b)
        so = (oa+ob) % self.__gfMaximum
        return self.getValue(so)
    def add(self, a, b):
        '''
            伽罗华有限域内加法
            a, b须为int
        '''
        va, vb = self.getValue(a), self.getValue(b)
        assert va and vb
        vab = va ^ vb
        return self.getOrder(vab)


    def getRates(self, pn): #   Galois field  
        if pn < 1: return    
        result = [0] * (pn + 1)
    
        for k in xrange(1, pn):
            for i in xrange(k, 0, -1):
                result[i] = self.add(result[i] + k, result[i-1])
            result[0] += k
        result[0] = self.mod(result[0])
        return map(lambda x: self.getValue(x), result)
    # def bufferEncodingTable(self):
    #     self.__rateLevelTab = {}
    #     for i in xrange(self.__gfBound):
    #         self.__rateLevelTab = self.getRates(i)
    # def encodeRates(self, pn):
    #     if self.__rateLevelTab:
    #         return self.__rateLevelTab[pn]
    #     else:
    #         return self.getRates(pn)